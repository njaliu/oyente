import six
import sys
#from z3 import *


def is_matched(a, b):
    return (a == b)


def is_greater_equal(a, b):
    return (a >= b)


def is_matched_with_parameter(a, b):
    return is_matched(a.operands[0], b.operands[0])


# compute similarity of two symbolic traces
def compute_trace_similarity(target, query):
    len_t = len(target)
    len_q = len(query)
    lencs, cs = lcs_opcode(target, query)
    target_sub = retrieve_subtrace_evm(cs, target, lencs, len_t, [])
    query_sub = retrieve_subtrace_evm(cs, query, lencs, len_q, [])

    if len(target_sub) == len(query_sub):
        matched, total = match_trace(target_sub, query_sub)
        six.print_("Matched: %d, Total: %d" % (matched, total))
        return float(lencs * matched / total)
    else:
        six.print_("Align ERROR: target length %d, query length %d" % (len(target_sub), len(query_sub)))
        return -1


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
            if is_matched_with_parameter(t_para[i], t_para[j]):
                t_dependency[i][j] = 1
                if is_matched_with_parameter(q_para[i], q_para[j]):
                    if q_dependency[i][j] == 0:
                        matched_check += 1
                    q_dependency[i][j] = 1

            if is_matched_with_parameter(q_para[i], q_para[j]):
                q_dependency[i][j] = 1
                if is_matched_with_parameter(t_para[i], t_para[j]):
                    if t_dependency[i][j] == 0:
                        matched_check += 1
                    t_dependency[i][j] = 1

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