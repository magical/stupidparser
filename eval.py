import math
import operator

if __name__ == '__main__' and __package__ is None:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    __package__ = 'stupidparser'
    __import__('stupidparser')

scope =\
    {"pi": math.pi
    ,"abs": abs
    ,"floor": math.floor
    ,"log": math.log
    ,"int": int
    ,"float": float
    }

operators = \
    {"+": operator.add
    ,"-": operator.sub
    ,"\N{MINUS SIGN}": operator.sub
    ,"*": operator.mul
    ,"\N{MULTIPLICATION SIGN}": operator.mul
    ,"/": operator.truediv
    ,"//": operator.floordiv
    ,"**": pow
    }

prefix_operators = \
    {"+": (lambda x: +x)
    ,"-": (lambda x: -x)
    ,"\N{MINUS SIGN}": (lambda x: -x)
    }


def eval(node):
    """ A depth-first evalutation function. """
    if node.id == '(literal)':
        return node.value
    elif node.id == '(name)':
        return scope[node.value]
    elif node.id == '(':
        name, args = node.children
        name = eval(name)
        args = [eval(v) for v in args]
        return name(*args)
    elif node.id in prefix_operators and len(node.children) == 1:
        value = eval(node.children[0])
        return prefix_operators[node.id](value)
    elif node.id in operators:
        values = [eval(v) for v in node.children]
        return operators[node.id](*values)
    else:
        raise ValueError('unknown node type', node)

def test():
    from .parse import Parser
    parser = Parser()
    def test_expr(expr, expected_value):
        ast = parser.parse(expr)
        value = eval(ast)
        assert value == expected_value, \
            "%s == %r; expected %r" % (ast, value, expected_value)
        print (expr, "==", value)

    tests =\
        [ ("1 + 2 + 3", 6)
        , ("500 * 6 + 1 * 5", 3005)
        , ("1 + 2 - 3 * 8", -21)
        , ("(1 + 2 - 3) * 8", 0)
        , ("5 ** 2", 25)
        , ("abs(0 - 4)", 4)
        , ("-4", -4)
        , ("\u2212 6", -6)
        , ("(1000 \u2212 7) // 13", 76)
        ]

    for expr, expected_value in tests:
        test_expr(expr, expected_value)

if __name__ == '__main__':
    test()



