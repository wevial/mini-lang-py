#####################################################################
#
# CAS CS 320, Fall 2013
# compile.py
# Weston Vial
#
#####################################################################

# Implements a compiler for the language defined for the midterm.

from random import randint
exec(open('parse.py').read())
exec(open('machine.py').read())

Leaf = str
Node = dict

def freshStr():
    return str(randint(0,10000000))

# Compiles Expression parse trees, converting them into machine code.
def compileExpression(env, e, heap):
    if type(e) == Node:
        for label in e:
            children = e[label]
            if label == "Number":
                n = children[0]
                heap = heap + 1
                return (["set " + str(heap) + " " + str(n)], heap, heap)

            if label == "Variable":
                x = children[0]
                frm = env[x]
                heap = heap + 1
                return (copy(frm, heap), heap, heap)

            if label == "Plus":
                e1 = children[0]
                e2 = children[1]
                heap1 = heap
                (insts1, addr1, heap2) = compileExpression(env, e1, heap1)
                (insts2, addr2, heap3) = compileExpression(env, e2, heap2)
                heap4 = heap3 + 1
                addrResult = heap4
                insts = insts1 \
                    + insts2 \
                    + copy(addr1, 1) \
                    + copy(addr2, 2) \
                    + ["add"] \
                    + copy(0, addrResult)
                return (insts, addrResult, heap4)

            if label == "Indexed":
                x = children[0]["Variable"][0]
                e = children[1]
                (instsE, addrE, heap) = compileExpression(env, e, heap)
                heap = heap + 1
                insts = instsE \
                    + ["set 1 " + str(env[x])] \
                    + copy(addrE, 2) \
                    + ["add"] \
                    + copyFromRef(0, heap)
                return (insts, heap, heap)

# Compiles Program parse trees, converting them into machine code.
def compileProgram(env, p, heap = 7):
    if type(p) == Leaf:
        if p == "End":
            return (env, [], heap)

    if type(p) == Node:
        for label in p:
            children = p[label]
            if label == "Print":
                e = children[0]
                p = children[1]
                (instsE, addr, heap) = compileExpression(env, e, heap)
                (env, instsP, heap) = compileProgram(env, p, heap)
                return (env, instsE + copy(addr, 5) + instsP, heap)

            if label == "AssignNumber":
                x = children[0]["Variable"][0]
                e = children[1]
                p = children[2]
                (instsE, addr, heap) = compileExpression(env, e, heap)
                env[x] = addr
                (env, instsP, heap) = compileProgram(env, p, heap)
                return (env, instsE + instsP, heap)

            if label == "AssignArray":
                x = children[0]["Variable"][0]
                e1 = children[1]
                e2 = children[2]
                e3 = children[3]
                p = children[4]
                heap1 = heap
                (instsE1, addr1, heap2) = compileExpression(env, e1, heap1)
                (instsE2, addr2, heap3) = compileExpression(env, e2, heap2)
                (instsE3, addr3, heap4) = compileExpression(env, e3, heap3)
                heap5 = heap4 + 1
                env[x] = heap5
                insts = instsE1 \
                    + instsE2 \
                    + instsE3 \
                    + copy(addr1, heap5) \
                    + copy(addr2, heap5 + 1) \
                    + copy(addr3, heap5 + 2)
                (env, instsP, heap6) = compileProgram(env, p, heap5 + 2)
                return (env, insts + instsP, heap6)

            if label == "For":
                x = children[0]["Variable"][0]
                p1 = children[1]
                p2 = children[2]
                fresh = freshStr()
                heap1 = heap + 1
                env1 = env
                insts = ["set " + str(env[x]) + " -1"] \
                    + ["set " + str(heap1) + " -1"] \
                    + ["label ForStart" + fresh] \
                    + copy(heap1, 1) \
                    + ["set 2 1"] \
                    + ["add"] \
                    + copy(0, heap1) \
                    + ["set 4 1"] \
                    + ["copy"] \
                    + ["set 2 -3"] \
                    + ["add"] \
                    + ["branch ForBody" + fresh + " 0"] \
                    + ["goto ForEnd" + fresh] \
                    + ["label ForBody" + fresh] \
                    + copy(heap1, env[x])
                (env2, instsBody, heap2) = compileProgram(env1, p1, heap1)
                instsBody = instsBody \
                    + ["goto ForStart" + fresh] \
                    + ["label ForEnd" + fresh]
                (env3, instsRest, heap3) = compileProgram(env2, p2, heap2)
                return (env3, insts + instsBody + instsRest, heap3)

# Tokenizes and parses the input string s and converts the parse tree
# into a set of machine code instructions
def compile(s):
    p = tokenizeAndParse(s)
    (env, insts, heap) = compileProgram({}, p)
    return insts

# Compiles the input string s and simulates the machine code.
def compileAndSimulate(s):
    return simulate(compile(s))

# eof
