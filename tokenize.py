import io
from collections import namedtuple

Token = namedtuple('Token', 'type, value')

def tokenizer(f):
    ch = ''
    def next():
        nonlocal ch
        ch = f.read(1)
        return ch
    next()

    operators = """
        <= < > >= ==
        + - \N{MINUS SIGN}
        * \N{MULTIPLICATION SIGN} / // mod
        **
        ( ) [ ] ,
        and or not
        if else
        """.split()
    operchars = set((c for oper in operators for c in oper if not c.isalpha()))

    while ch:
        if ch.isdigit():
            number = ch
            while next().isdigit():
                number += ch
            assert not ch.isalpha(), ("bad number", number)
            yield Token('number', int(number))
        elif ch.isalpha():
            name = ch
            while next().isalnum():
                name += ch

            if name in operators:
                yield Token('operator', name)
            else:
                yield Token('name', name)
        elif ch.isspace():
            while next().isspace():
                pass
        elif ch in operchars:
            oper = ch
            while next() in operchars:
                oper += ch
            assert oper in operators, ("invalid operator", oper)
            yield Token('operator', oper)
        else:
            assert False, ("unknown character", ch)


def test():
    strings = """\
1 + 2
3 + 4 * 6

1 and 5
(5 and 6) and 7
""".splitlines()

    for string in strings:
        if not string:
            continue
        print(string)
        f = io.StringIO(string)
        for token in tokenizer(f):
            print(" ", token)
        print()

def test_bad_strings():
    strings = """\
1.6
###
5and7
<=>
""".splitlines()

    for string in strings:
        if not string:
            continue
        print(string)
        f = io.StringIO(string)
        try:
            tokens = list(tokenizer(f))
        except Exception as e:
            print(repr(e))
        else:
            for token in tokens:
                print(" ", token)
        print()

if __name__ == '__main__':
    test()
    test_bad_strings()
