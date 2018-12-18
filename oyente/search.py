import six
import sys
#from z3 import *

def is_matched(a, b):
    return (a == b)

def is_greater_equal(a, b):
	return (a >= b)


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