import six
import evaluate
import math
from trace import Trace
from z3 import *


# Constants
PILATUS_INFO = "Pilatus Info: "
SEARCH_SIZE = 5
VECTOR = {"JUMP": 0,
          "JUMPI": 1,
          "SHA3": 2,
          "MLOAD": 3,
          "MSTORE": 4,
          "SLOAD": 5,
          "SSTORE": 6,
          "CALL": 7}


def is_matched(a, b):
    return a == b


def is_greater_equal(a, b):
    return a >= b


def is_matched_with_parameter(a, b):
    return is_matched(a.operands[0], b.operands[0])


# main entry of vulnerability search
def search_vulnerability(traces, goal):
    # EC: Evil Callee, FR: Front Runner, BG: Broken Guard
    vulnerabilities = {"EC": [], "FR": [], "BG": []}
    n_call, call_traces, n_state, state_traces = group_traces(traces)

    if n_call == 0:
        six.print_(PILATUS_INFO + "no message calls!")
        return None
    else:
        # search for EC
        if goal == "EC":
            ec_rank_list = rank_trace(evaluate.EVIL_CALLEE, call_traces, SEARCH_SIZE)
            for tup in ec_rank_list:
                idx = tup[0]
                vulnerabilities["EC"].append(call_traces[idx])
            six.print_(PILATUS_INFO + "%d Evil Callee found" % len(vulnerabilities["EC"]))

        # search for FR
        if goal == "FR":
            for call_trace in call_traces:
                len_cs, cs = lcs_opcode(evaluate.EVIL_CALLEE, call_trace)
                sub_trace = retrieve_subtrace_evm(cs, evaluate.EVIL_CALLEE, len_cs, len(evaluate.EVIL_CALLEE), [])
                unmatched_idx, unmatched = retrieve_unmatched_evm(evaluate.EVIL_CALLEE, sub_trace)
                len_fr, fr_traces = generate_cross_tx_traces(state_traces, call_trace, unmatched)
                fr_rank_list = rank_trace(evaluate.EVIL_CALLEE, fr_traces, SEARCH_SIZE)
                for tup in fr_rank_list:
                    idx = tup[0]
                    vulnerabilities["FR"].append(fr_traces[idx])
                six.print_(PILATUS_INFO + "%d Front Runner found" % len(vulnerabilities["FR"]))

        # search for BG
        if goal == "BG":
            for call_trace in call_traces:
                len_cs, cs = lcs_opcode(evaluate.EVIL_CALLEE, call_trace)
                sub_trace = retrieve_subtrace_evm(cs, evaluate.EVIL_CALLEE, len_cs, len(evaluate.EVIL_CALLEE), [])
                unmatched_idx, unmatched = retrieve_unmatched_evm(evaluate.EVIL_CALLEE, sub_trace)
                len_bg, bg_traces = generate_cross_tx_traces(state_traces, call_trace, unmatched)
                bg_rank_list = rank_trace(evaluate.EVIL_CALLEE, bg_traces, SEARCH_SIZE)
                for tup in bg_rank_list:
                    idx = tup[0]
                    vulnerabilities["FR"].append(bg_traces[idx])
                six.print_(PILATUS_INFO + "%d Broken Guard found" % len(vulnerabilities["BG"]))

        return vulnerabilities["EC"]


# generate candidates traces for bug search
def group_traces(traces):
    call_traces = []
    state_traces = []
    for trace in traces:
        if trace.get_callable():
            call_traces.append(trace)
        else:
            state_traces.append(trace)

    if len(call_traces) == 0:
        six.print_("ERROR: no callable traces generated")
        return None
    elif len(state_traces) == 0:
        six.print_(PILATUS_INFO + "no state traces generated")
        return len(call_traces), call_traces, 0, []
    else:
        return len(call_traces), call_traces, len(state_traces), state_traces


# generate a sorted list of cross transaction traces
def generate_cross_tx_traces(state_traces, call_trace, unmatched_trace):
    generated = []
    distance_dict = {}
    for i in range(len(state_traces)):
        st = state_traces[i]
        d = calculate_trace_distance(st, unmatched_trace)
        if d != -1:
            distance_dict[i] = d

    dist_sorted_tup = sorted(distance_dict.items(), key=lambda x: x[1])
    for tup in dist_sorted_tup:
        s = state_traces[tup[0]]
        if is_mergable(s, call_trace):
            generated.append(merge_trace(s, call_trace))
        else:
            six.print_(PILATUS_INFO + "traces at line %s and %s cannot be merged." % (s.get_lines(), call_trace.get_lines()))

    return len(generated), generated


# merge two symbolic traces
def merge_trace(t1, t2):
    t = Trace()
    t.set_trace(t1.get_trace() + t2.get_trace())
    t.set_path_conditions(t1.get_path_conditions() + t2.get_path_conditions())
    t.set_callable(t1.get_callable() or t2.get_callable())
    t.set_lines(t1.get_lines() + t2.get_lines())

    return t


# check if two traces can be merged
def is_mergable(t1, t2):
    merged_path_conditions = t1.get_path_conditions() + t2.get_path_conditions()
    solver = Solver()
    solver.push()
    for c in merged_path_conditions:
        solver.add(c)

    if solver.check() == unsat:
        solver.pop()
        return False

    solver.pop()

    return True


# rank query_traces based on their similarity to target and pick top_n
def rank_trace(target, query_traces, top_n):
    n = len(query_traces)
    len_t = len(target.get_trace())
    jaccard = {}
    for i in range(n):
        len_q = len(query_traces[i].get_trace())
        len_cs, matched_prop, total_prop = compute_trace_similarity(target.get_trace(), query_traces[i].get_trace())
        cs_prop = (float)(len_cs * matched_prop / total_prop)
        jaccard[i] = (float) (cs_prop / (len_t + len_q - cs_prop))

    rank = sorted(jaccard.items(), key= lambda x:x[1], reverse=True)
    if len(rank) < top_n:
        six.print_("WARN: top %d is larger than rank length %d" % (top_n, len(rank)))
        return rank
    else:
        return rank[:top_n]


# compute similarity of two symbolic traces
def compute_trace_similarity(target, query):
    len_t = len(target)
    len_q = len(query)
    len_cs, cs = lcs_opcode(target, query)
    target_sub = retrieve_subtrace_evm(cs, target, len_cs, len_t, [])
    query_sub = retrieve_subtrace_evm(cs, query, len_cs, len_q, [])

    if len(target_sub) == len(query_sub):
        matched, total = match_trace(target_sub, query_sub)
        six.print_("Matched: %d, Total: %d" % (matched, total))
        return (len_cs, matched, total)
        #return float(len_cs * matched / total)
    else:
        six.print_("Align ERROR: target length %d, query length %d" % (len(target_sub), len(query_sub)))
        return -1


# calculate Euclidean Distance of two given traces
# trace vector: [JUMP, JUMPI, SHA3, MLOAD, MSTORE, SLOAD, SSTORE, CALL]
def calculate_trace_distance(candidate, unmatched):
    v_c = trace2vec(candidate)
    v_u = trace2vec(unmatched)
    dist_square = 0
    if len(v_c) != len(v_u):
        six.print_("ERROR: vector length inconsistent. candidate: %d, unmatched: %d" % (len(v_c), len(v_u)))
        return -1
    for i in range(len(v_c)):
        dist_square += math.pow(abs(v_c[i] - v_u[i]), 2)
    dist = math.sqrt(dist_square)

    return dist


# convert trace to numeric vector
def trace2vec(trace):
    v = [0,0,0,0,0,0,0,0]
    for instr in trace.trace:
        op = instr.opcode
        if op == "JUMP":
            v[VECTOR["JUMP"]] += 1
        elif op == "JUMPI":
            v[VECTOR["JUMPI"]] += 1
        elif op == "SHA3":
            v[VECTOR["SHA3"]] += 1
        elif op == "MLOAD":
            v[VECTOR["MLOAD"]] += 1
        elif op == "MSTORE":
            v[VECTOR["MSTORE"]] += 1
        elif op == "SLOAD":
            v[VECTOR["SLOAD"]] += 1
        elif op == "SSTORE":
            v[VECTOR["SSTORE"]] += 1
        elif op == "CALL":
            v[VECTOR["CALL"]] += 1
        else:
            six.print_("ERROR: invalid opcode %s" % instr.opcode)

    return v


# match two symbolic traces by aligning their opcodes and parameters
def match_trace(target, query):
    len_total = len(target)
    t_para = [ o for o in target if len(o.operands) > 0]
    q_para = [ o for o in query if len(o.operands) > 0]

    if len(t_para) != len(q_para):
        six.print_("Align ERROR: target parameter length %d, query parameter length %d" % (len(t_para), len(q_para)))
        return None

    len_para = len(t_para)
    len_must = len_total - len_para

    t_dependency = [[0 for i in range(len_para)] for j in range(len_para)]
    q_dependency = [[0 for i in range(len_para)] for j in range(len_para)]

    matched_check = 0
    total = len_total * (len_total - 1) / 2
    matched_must = len_must * (len_must - 1) / 2

    for i in range(len_para):
        for j in range(i+1, len_para):
            if is_matched_with_parameter(t_para[i], t_para[j]) == is_matched_with_parameter(q_para[i], q_para[j]):
                matched_check += 1
                if is_matched_with_parameter(t_para[i], t_para[j]):
                    t_dependency[i][j] = 1
                if is_matched_with_parameter(q_para[i], q_para[j]):
                    q_dependency[i][j] = 1

    return (matched_check + matched_must), total


# retrieve a symbol sub-trace from full_trace for an input opcode_list
def retrieve_subtrace_evm(opcode_list, full_trace, m, n, picked):
    if m == 0 or n == 0:
        return picked

    if is_matched(opcode_list[m-1], full_trace[n-1].opcode):
        picked.insert(0, full_trace[n-1])
        #print picked
        return retrieve_subtrace_evm(opcode_list, full_trace, m-1, n-1, picked)

    return retrieve_subtrace_evm(opcode_list, full_trace, m, n-1, picked)


# retrieve unmatched EVM trace
def retrieve_unmatched_evm(origin, cs):
    first = cs[0].opcode
    n = len(origin.trace)
    for i in range(n):
        instr = origin.trace[n-1-i].opcode
        if is_matched(first, instr):
            unmatched_idx = n-1-i
            return unmatched_idx, origin.trace[0:unmatched_idx]
    return -1, []


# retrieve a sub-trace from a full_trace
def retrieve_subtrace(opcode_list, full_trace, m, n, picked):
    if m == 0 or n == 0:
        return picked

    if is_matched(opcode_list[m-1], full_trace[n-1]):
        picked.insert(0, full_trace[n-1])
        #print picked
        return retrieve_subtrace(opcode_list, full_trace, m-1, n-1, picked)

    return retrieve_subtrace(opcode_list, full_trace, m, n-1, picked)

#print retrieve_subtrace("abc", "abdefc", 3, 6, [])


# longest common subsequence (LCS) search
# input as list, python 2.7
def lcs_opcode(s1, s2):
    matrix = [[ [] for x in range(len(s2))] for x in range(len(s1))]
    for i in range(len(s1)):
        for j in range(len(s2)):
            if is_matched(s1[i].opcode, s2[j].opcode):
                if i == 0 or j == 0:
                    matrix[i][j] = [str(s1[i].opcode)]
                else:
                    to_append = matrix[i-1][j-1][:] # copy
                    to_append.append(str(s1[i].opcode))
                    matrix[i][j] = to_append
            else:
                matrix[i][j] = max(matrix[i-1][j], matrix[i][j-1], key=len)
                '''
                if len(matrix[i-1][j]) > 0 and len(matrix[i][j-1]) > 0:
                    if is_greater_equal(matrix[i-1][j][0], matrix[i][j-1][0]):
                        pick = matrix[i-1][j]
                    else:
                        pick = matrix[i][j-1]
                else:
                    if len(matrix[i-1][j]) == 0:
                        pick = matrix[i][j-1]
                    elif len(matrix[i][j-1]) == 0:
                        pick = matrix[i-1][j]
                matrix[i][j] = pick[:]
                '''

    cs = matrix[-1][-1]

    return len(cs), cs


# input as list
def lcs_list(s1, s2):
    matrix = [[ [] for x in range(len(s2))] for x in range(len(s1))]
    for i in range(len(s1)):
        for j in range(len(s2)):
            if s1[i] == s2[j]:
                if i == 0 or j == 0:
                    matrix[i][j] = [str(s1[i])]
                else:
                    to_append = matrix[i-1][j-1].copy()
                    to_append.append(str(s1[i]))
                    matrix[i][j] = to_append
            else:
                if len(matrix[i-1][j]) > 0 and len(matrix[i][j-1]) > 0:
                    if matrix[i-1][j][0] >= matrix[i][j-1][0]:
                        pick = matrix[i-1][j]
                    else:
                        pick = matrix[i][j-1]
                else:
                    if len(matrix[i-1][j]) == 0:
                        pick = matrix[i][j-1]
                    elif len(matrix[i][j-1]) == 0:
                        pick = matrix[i-1][j]
                matrix[i][j] = pick.copy()

    cs = matrix[-1][-1]

    return len(cs), cs


# input as string
def lcs_string(s1, s2):
    matrix = [["" for x in range(len(s2))] for x in range(len(s1))]
    for i in range(len(s1)):
        for j in range(len(s2)):
            if s1[i] == s2[j]:
                if i == 0 or j == 0:
                    matrix[i][j] = str(s1[i])
                else:
                    matrix[i][j] = matrix[i-1][j-1] + str(s1[i])
            else:
                matrix[i][j] = max(matrix[i-1][j], matrix[i][j-1], key=len)

    cs = matrix[-1][-1]

    return len(cs), cs

#print(lcs_list("ABfdsfC", "AadfadfC"))
#print(lcs([1,4,5,6,3,6,4], [2,4,5,6,2,6,7]))  