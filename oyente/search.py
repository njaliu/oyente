import six
import sys
#from z3 import *

# longest common subsequence (LCS) search
'''
def lcs_opcode(target, query, maxlen):
	return 0

def lcs(a,b):
	lena=len(a)
	lenb=len(b)
	c=[[0 for i in range(lenb+1)] for j in range(lena+1)]
	flag=[[0 for i in range(lenb+1)] for j in range(lena+1)]
	for i in range(lena):
		for j in range(lenb):
			if a[i]==b[j]:
				c[i+1][j+1]=c[i][j]+1
				flag[i+1][j+1]='ok'
			elif c[i+1][j]>c[i][j+1]:
				c[i+1][j+1]=c[i+1][j]
				flag[i+1][j+1]='left'
			else:
				c[i+1][j+1]=c[i][j+1]
				flag[i+1][j+1]='up'
	return c,flag
 
def printLcs(flag,a,i,j):
	if i==0 or j==0:
		return
	if flag[i][j]=='ok':
		printLcs(flag,a,i-1,j-1)
		print(a[i-1]+'')
	elif flag[i][j]=='left':
		printLcs(flag,a,i,j-1)
	else:
		printLcs(flag,a,i-1,j)
		
a='ABCBDAB'
b='BDCABA'
c,flag=lcs(a,b)
for i in c:
	print(i)
print('')
for j in flag:
	print(j)
print('')
printLcs(flag,a,len(a),len(b))
print('')
'''

def is_matched(a, b):
	return (a == b)

def lcs_opcode(s1, s2):
    matrix = [["" for x in range(len(s2))] for x in range(len(s1))]
    for i in range(len(s1)):
        for j in range(len(s2)):
            if is_matched(s1[i].opcode, s2[j].opcode):
                if i == 0 or j == 0:
                    matrix[i][j] = s1[i].opcode + ', '
                else:
                    matrix[i][j] = matrix[i-1][j-1] + s1[i].opcode + ', '
            else:
                matrix[i][j] = max(matrix[i-1][j], matrix[i][j-1], key=len)

    cs = matrix[-1][-1]

    return len(cs), cs

def lcs(s1, s2):
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

#print(lcs("ABCBDAB", "BDCABA"))
#print(lcs([1,4,5,6,3,6,4], [2,4,5,6,2,6,7]))  

def LCS_new(s1, s2):
    size1 = len(s1) + 1
    size2 = len(s2) + 1

    chess = [[["", 0] for j in list(range(size2))] for i in list(range(size1))]
    for i in list(range(1, size1)):
        chess[i][0][0] = s1[i - 1]
    for j in list(range(1, size2)):
        chess[0][j][0] = s2[j - 1]
    print("Init data: ")
    print(chess)
    for i in list(range(1, size1)):
        for j in list(range(1, size2)):
            if s1[i - 1] == s2[j - 1]:
                chess[i][j] = ['TL', chess[i - 1][j - 1][1] + 1]
            elif chess[i][j - 1][1] > chess[i - 1][j][1]:
                chess[i][j] = ['L', chess[i][j - 1][1]]
            else:
                chess[i][j] = ['T', chess[i - 1][j][1]]
    print("Result: ")
    print(chess)
    i = size1 - 1
    j = size2 - 1
    s3 = []
    while i > 0 and j > 0:
        if chess[i][j][0] == 'TL':
            s3.append(chess[i][0][0])
            i -= 1
            j -= 1
        if chess[i][j][0] == 'L':
            j -= 1
        if chess[i][j][0] == 'T':
            i -= 1
    s3.reverse()
    print("LCS: %s" % s3)

#LCS_new("ABCBDAB", "BDCABA")
LCS_new([4,2,4,4,2,1,3,5,7,9], [3,4,2,1,5,7,2])