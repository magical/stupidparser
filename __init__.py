
from .parse import Parser
from .eval import eval as eval_ast

def eval(expr):
    """A convienience function for evaluating a string expression."""
    parser = Parser()
    ast = parser.parse(expr)
    value = eval_ast(ast)

    return value
