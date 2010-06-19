# Top Down Operator Precedence parser
# http://javascript.crockford.com/tdop/tdop.html
# http://effbot.org/zone/simple-top-down-parsing.htm

# nud = null denotation
# led = left denotation
# lbp = left binding power

# the higher the binding power, the more tightly the oper binds

import io
from functools import wraps, partial
from collections import namedtuple

if __name__ == '__main__' and __package__ is None:
    import sys, os
    __package__ = 'parser'
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    import parser

from .tokenize import tokenizer

class ParseError(Exception):
    pass

class Registry:
    def __init__(self):
        self._nud = {}
        self._led = {}
        self.lbp = {}

    def nud(self, name):
        """decorator for adding a nud function"""
        def inner(func):
            self._nud[name] = func
            if name not in self.lbp:
                self.lbp[name] = 0
            return func
        return inner

    def led(self, name, lbp=0):
        """decorator for adding a led function"""
        def inner(func):
            self._led[name] = func
            self.lbp[name] = lbp
            return func
        return inner

    def default_nud(self, *args):
        raise ParseError("Undefined")

    def default_led(self, *args):
        raise ParseError("Missing operator")

    def get_nud(self, name):
        return self._nud.get(name, self.default_nud)

    def get_led(self, name):
        return self._led.get(name, self.default_led)

Symbol = namedtuple('Symbol', 'id, value')

class LiteralNode:
    def __init__(self, id, value):
        self.id = id
        self.value = value

    def __str__(self):
        return "(literal %r)" % self.value

class TreeNode:
    def __init__(self, id, children):
        self.id = id
        self.children = children

    def __str__(self):
        def fmt(v):
            if isinstance(v, list):
                return '[' + ', '.join(map(fmt, v)) + ']'
            else:
                return str(v)
        return "(%r %s)" % (self.id, fmt(self.children))


class Parser:
    def __init__(self):
        self.registry = Registry()
        self.define_symbols()

    def parse(self, input):
        self.tokenizer = tokenizer(io.StringIO(input))
        self._next()
        return self.expression()

    def expression(self, rbp=0):
        token = self.token
        self._next()
        left = self.registry.get_nud(token.id)(token)
        while rbp < self.registry.lbp[self.token.id]:
            token = self.token
            self._next()
            left = self.registry.get_led(token.id)(token, left)
        return left

    def _next(self, id=None):
        """get the next token. if id is provided, verify that the current
        token matches the id."""
        if id is not None and id != self.token.id:
            raise ParseError("Expected %s" % id)
        try:
            token = self.tokenizer.__next__()
        except StopIteration:
            return Symbol('(end)', None)
        if token.type == 'operator':
            self.token = Symbol(token.value, None)
        elif token.type == 'number':
            self.token = Symbol('(literal)', token.value)
        elif token.type == 'name':
            self.token = Symbol('(name)', token.value)
        else:
            raise ParseError("Unknown token", token)

    def infix(self, id, lbp):
        @self.registry.led(id, lbp)
        def led(symbol, left):
            return TreeNode(id, [left, self.expression(lbp)])

    def infixr(self, id, lbp):
        @self.registry.led(id, lbp)
        def led(symbol, left):
            return TreeNode(id, [left, self.expression(lbp-1)])

    def prefix(self, id, rbp):
        @self.registry.nud(id)
        def nud(symbol):
            return TreeNode(id, [self.expression(rbp)])

    def symbol(self, id):
        self.registry.lbp[id] = 0

    def literal(self, id):
        @self.registry.nud(id)
        def nud(symbol):
            return LiteralNode(id, symbol.value)

    def define_symbols(self):
        symbol = self.symbol
        literal = self.literal
        infix = self.infix
        infixr = self.infixr
        prefix = self.prefix

        symbol("(end)")
        symbol(")")
        symbol(",")

        literal('(literal)')
        literal('(name)')

        infix("or", 10)
        infix("and", 11)
        prefix("not", 12)

        infix("==", 20)
        infix("!=", 20)
        infix("<", 20)
        infix(">", 20)
        infix("<=", 20)
        infix("=>", 20)

        infix("+", 30)
        infix("-", 30)
        infix("\N{MINUS SIGN}", 30)

        infix("*", 40)
        infix("/", 40)
        infix("//", 40)

        infixr("**", 50)

        prefix("+", 70)
        prefix("-", 70)
        prefix("\N{MINUS SIGN}", 70)

        # parentheses
        @self.registry.nud("(")
        def nud(symbol):
            value = self.expression()
            self._next(")")
            return value

        # function call
        @self.registry.led("(", 10)
        def led(symbol, left):
            assert left.id != '(literal)'
            values = []
            while self.token.id != ')':
                values.append(self.expression())
                if self.token.id == ',':
                    self._next(',')
            self._next(")")
            return TreeNode("(", [left, values])

def test():
    parser = Parser()
    print(parser.parse("1 + 1"))
    print(parser.parse("1 * 7 * 9"))
    print(parser.parse("1 + 2 * 3"))
    print(parser.parse("int(2)"))
    print(parser.parse("abs(2 - 7)"))

if __name__ == '__main__':
    test()
