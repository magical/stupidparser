import math
import operator

if __name__ == '__main__' and __package__ is None:
    __package__ = 'stupidparser'
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    __import__('stupidparser')

scope =\
    {"pi": math.pi
    ,"abs": abs
    ,"floor": math.floor
    ,"log": math.log
    ,"int": int
    ,"float": float
    ,"sum": (lambda *args: sum(args))
    ,"true": True
    ,"false": False
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
    ,"==": operator.eq
    ,"!=": operator.ne
    ,"<": operator.lt
    ,">": operator.gt
    ,"<=": operator.le
    ,">=": operator.ge
    ,"not": operator.not_
    }

prefix_operators = \
    {"+": operator.pos
    ,"-": operator.neg
    ,"\N{MINUS SIGN}": operator.neg
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
        args = map(eval, args)
        return name(*args)
    elif node.id == 'and':
        assert len(node.children) == 2
        first = eval(node.children[0])
        if first:
            return eval(node.children[1])
        else:
            return first
    elif node.id == 'or':
        assert len(node.children) == 2
        first = eval(node.children[0])
        if first:
            return first
        else:
            return eval(node.children[1])
    elif node.id == 'not':
        assert len(node.children) == 1
        return not eval(node.children[0])
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
        #print(ast)
        value = eval(ast)
        #assert type(value) == type(expected_value)
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
        , ("sum(5, 5)", 10)
        , ("sum(1, 2, 3, 4)", 10)
        , ("5 == 5", True)
        , ("5 == 6", False)
        , ("(1 == 1) and (2 == 2)", True)
        , ("(1 == 2) and (2 == 2)", False)
        , ("(1 == 1) and (1 == 2)", False)
        , ("(1 == 2) and (1 == 2)", False)
        , ("true and true", True)
        , ("false and true", False)
        , ("true and false", False)
        , ("false and false", False)
        , ("not 1 == 1", False)
        , ("true", True)
        , ("1", 1)
        , ("not true", False)
        , ("true or false", True)
        , ("true and false or 5", 5)
        , ("0 or true and false", 0)
        , ("(0 or true) and false", False)
        #, ("1 == 2 == 3", True)
        , ("5 < 6", True)
        , ("5 > 6", False)
        , ("5 < 5", False)
        , ("5 <= 5", True)
        , ("-1 < 4", True)
        ]

    for expr, expected_value in tests:
        test_expr(expr, expected_value)

if __name__ == '__main__':
    test()



