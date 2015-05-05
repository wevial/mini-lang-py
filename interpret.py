#####################################################################
#
# CAS CS 320, Fall 2013
# interpret.py
# Weston Vial 
#
#####################################################################

# Implements an interpreter for the language defined for the midterm.

exec(open("parse.py").read())

Node = dict
Leaf = str

# Evaluates Expression parse trees.
def evaluate(env, e):
    if type(e) == Node:
        for label in e:
            children = e[label]
            if label == "Number":
                n = children[0]
                return n

            if label == "Variable":
                x = children[0]
                if x in env:
                    return env[x]
                else:
                    print(x + "is unbound.")

            if label == "Indexed":
                x = children[0]["Variable"][0]
                e = children[1]
                k = evaluate(env, e)
                if k >= 0 and k <= 2:
                    n = env[x]["Array"][k]["Number"][0]
                    return n
                else:
                    print("Array out of bounds")

            if label == "Plus":
                t1 = children[0]
                t2 = children[1]
                n1 = evaluate(env, t1)
                n2 = evaluate(env, t2)
                return n1 + n2

# Executes Program parse trees.
def execute(env, p):
    if type(p) == Leaf:
        if p == "End":
            return (env, [])
    elif type(p) == Node:
        for label in p:
            children = p[label]
            if label == "AssignNumber":
                x = children[0]["Variable"][0]
                e = children[1]
                p = children[2]
                n = evaluate(env, e)
                env[x] = n
                (env, o) = execute(env, p)
                return (env, o)

            if label == "AssignArray":
                x = children[0]["Variable"][0]
                e0 = children[1]
                e1 = children[2]
                e2 = children[3]
                p = children[4]
                # Get values of array
                n0 = evaluate(env, e0)
                n1 = evaluate(env, e1)
                n2 = evaluate(env, e2)
                env[x] = {"Array" : [{"Number": [n0]}, {"Number": [n1]}, {"Number": [n2]}]}
                (env, o) = execute(env, p)
                return (env, o)

            if label == "Print":
                e = children[0]
                p = children[1]
                n = evaluate(env, e)
                if type(n) == type({}):
                    print("Cannot print array")
                else:
                    (env, o) = execute(env, p)
                    return (env, [n] + o)

            if label == "For":
                x = children[0]["Variable"][0]
                p1 = children[1]
                p2 = children[2]
                env1 = env
                # Loop Body
                env1[x] = 0
                (env2, o1) = execute(env1, p1)
                env2[x] = 1
                (env3, o2) = execute(env2, p1)
                env3[x] = 2
                (env4, o3) = execute(env3, p1)
                # Rest
                (env5, o4) = execute(env4, p2)
                return (env5, o1 + o2 + o3 + o4)

# Tokenizes and parses the input string s. The parse tree is then executed and its output is returned.
def interpret(s):
    ptree = tokenizeAndParse(s)
    (env, output) = execute({}, ptree)
    return output

# eof
