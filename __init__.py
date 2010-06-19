# Copyright 2010 by magical
#
# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# http://sam.zoy.org/wtfpl/COPYING for more details.

from .parse import Parser
from .eval import eval as eval_ast

def eval(expr):
    """A convienience function for evaluating a string expression."""
    parser = Parser()
    ast = parser.parse(expr)
    value = eval_ast(ast)

    return value
