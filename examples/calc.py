'''
A slightly extended calculator based on the original Rply example
'''

from rply import ParserGenerator, LexerGenerator 

# Define tokens as constants to avoid typos
PLUS = "PLUS"
MINUS = "MINUS"
TIMES = "TIMES"
DIVIDES = "DIVIDES"
NUMBER = "NUMBER"
LPARENS = "LPARENS"
RPARENS = "RPARENS"


lg = LexerGenerator()
# Add takes a rule name, and a regular expression that defines the rule.

lg.add(PLUS, r"\+")
lg.add(MINUS, r"-")
lg.add(TIMES, r"\*")
lg.add(DIVIDES, r"/")
lg.add(NUMBER, r"\d+")
lg.add(LPARENS, r"\(")
lg.add(RPARENS, r"\)")

lg.ignore(r"\s+")

# This is a list of the token names. precedence is an optional list of
# tuples which specifies order of operation for avoiding ambiguity.
# precedence must be one of "left", "right", "nonassoc".
# cache_id is an optional string which specifies an ID to use for
# caching. It should *always* be safe to use caching,
# RPly will automatically detect when your grammar is
# changed and refresh the cache for you.
pg = ParserGenerator([NUMBER,
                      PLUS, MINUS, TIMES, DIVIDES,
                      LPARENS, RPARENS,
                      ],

# Precedence is defined from lower to higher
        precedence=[("left", [PLUS, MINUS]), 
                    ("left", [TIMES, DIVIDES])], 
        cache_id="myparser")

# TODO: Production precedence example?
@pg.production("main : expr")
def main(p):
    return p[0]

@pg.production("expr : LPARENS expr RPARENS")
def expr_parens(p):
    return p[1]

@pg.production("expr : expr PLUS expr")
@pg.production("expr : expr MINUS expr")
@pg.production("expr : expr TIMES expr")
@pg.production("expr : expr DIVIDES expr")
def expr_op(p):
    lhs = p[0]
    rhs = p[2]
    op = p[1].gettokentype()
    if op == PLUS:
        return lhs + rhs
    elif op == MINUS:
        return lhs - rhs
    elif op == TIMES:
        return lhs * rhs
    elif op == DIVIDES:
        return lhs // rhs # Note: Integer division
    else:
        raise AssertionError("This is impossible, abort the time machine!")

@pg.production("expr : NUMBER")
def expr_num(p):
    return int(p[0].getstr())

@pg.error
def error_handler(token):
    raise ValueError("Ran into a %s where it wasn't expected" % token.gettokentype())

# Instantiate the Lexer and Parser
lexer = lg.build()
parser = pg.build()

# Simple examples
assert parser.parse(lexer.lex("1 + 3 - 2+12-32")) == -18
assert parser.parse(lexer.lex("1 * 3")) == 3
assert parser.parse(lexer.lex("1 * 3 + 2")) == 5
assert parser.parse(lexer.lex("1 + 2 * 3")) == 7
assert parser.parse(lexer.lex("1 + 2 / 3")) == 1
assert parser.parse(lexer.lex("2 * 6 / 3")) == 4
assert parser.parse(lexer.lex("2 * 6 + 3")) == 15
assert parser.parse(lexer.lex("(2 * 6) + 3")) == 15
assert parser.parse(lexer.lex("2 * (6 + 3)")) == 18
assert parser.parse(lexer.lex("(2 * (6 + 3))")) == 18


# Example Parser Error
try:
    parser.parse(lexer.lex("1 + 3 - 2 6 12-32"))
except ValueError:
    pass
else:
    assert False
