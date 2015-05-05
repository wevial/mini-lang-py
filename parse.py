#####################################################################
#
# CAS CS 320, Fall 2013
# parse.py
# Weston Vial 
#
#####################################################################

# A parser for the simple language defined for the Midterm.

import re

# Variable
def variable(tokens, top = True):
	if re.compile(r"[a-z][A-Za-z]*").match(tokens[0]):
		return ({"Variable": [tokens[0]]}, tokens[1:])
 
# Number
def number(tokens, top = True):
	if re.compile(r"(0|[1-9][0-9]*)").match(tokens[0]):
		return ({"Number": [int(tokens[0])]}, tokens[1:])

# Expression
def expression(tokens, top = True):
	r = expressionLeft(tokens, False)
	if not r is None:
		(e1, tokens) = r
		if len(tokens) > 0 and tokens[0] == "+":
			r = expression(tokens[1:], False)
			if not r is None:
				(e2, tokens) = r
				return ({"Plus": [e1,e2]}, tokens)
		else:
			return (e1, tokens)
	
def expressionLeft(tokens, top = True):
	r = number(tokens, False)
	if not r is None:
		return r

	r = variable(tokens, False)
	if not r is None:
		(e1, tokens) = r
		if len(tokens) > 0 and tokens[0] == "[":
			r = expression(tokens[1:], False)
			if not r is None:
				(e2, tokens) = r
				if len(tokens) > 0 and tokens[0] == "]":
					return ({"Indexed": [e1,e2]}, tokens[1:])
		else:
			return r

# Program
def program(tokens, top = True):
	seqs = [ \
		("AssignNumber", ["number", variable, ":=", expression, ";", program]), \
		("AssignArray", ["array", variable, ":=", "[", expression, ",",  expression, ",", expression, "]", ";", program]), \
		("Print", ["print", expression, ";", program]), \
		("For", ["for", variable, "{", program, "}", program]), \
		("End", []) \
	]

	if len(tokens) == 0:
		return ("End", [])

	for (label, seq) in seqs:
		ss = []
		es = []
		for x in seq:
			if type(x) == type(""):
				if tokens[0] == x:
					tokens = tokens[1:]
					ss = ss + [x]
				else:
					break
			else:
				r = x(tokens, False)
				if not r is None:
					(e, tokens) = r
					es = es + [e]

		if len(ss) + len(es) == len(seq):
			if not top or len(tokens) == 0:
				return ({label: es} if len(es) > 0 else label, tokens)

# Tokenizes the input string s and then parses it. Returns the parse tree.
def tokenizeAndParse(s):
	print(s)
	tokens = re.split(r"(\s+|number|array|print|for|:=|;|\[|\]|,|{|}|\+)", s)
	tokens = [t for t in tokens if not t.isspace() and not t == ""]
	(p, tokens) = program(tokens)
	return p

#eof
