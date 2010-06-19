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
            # Okay, okay: this is probably a number (if it's not, we throw
            # an error).  If it starts with '0', the next character might
            # specify a base--but it also might continue on with decimal
            # digits, or stop entirely (for the number 0).  Unlike in C,
            # a leading 0 does not always mean octal.
            base = 10
            digits = "0123456789"

            number = ''

            if ch == '0':
                number += ch # a leading 0 won't hurt
                next()
                if ch == 'x':
                    next()
                    base = 16
                    digits = "0123456789abcdef"
                elif ch == 'o' or ch == 't':
                    next()
                    base = 8
                    digits = "01234567"
                elif ch == 'b':
                    next()
                    base = 2
                    digits = "01"

            while ch and ch in digits:
                number += ch
                next()

            # a number must be followed by space or punctuation
            assert not ch.isalnum(), ("bad number", number)

            yield Token('number', int(number, base))
        elif ch.isalpha():
            # A name. Could be a function or constant or who knows.
            name = ch
            while next().isalnum():
                name += ch

            # Let's make sure this isn't actually an operator
            if name in operators:
                yield Token('operator', name)
            else:
                yield Token('name', name)
        elif ch.isspace():
            # Whitespace
            while next().isspace():
                pass
        elif ch in operchars:
            # An operator
            oper = ch
            while next() in operchars:
                oper += ch
            assert oper in operators, ("invalid operator", oper)
            yield Token('operator', oper)
        else:
            assert False, ("unknown character", ch)


def test():
    # these should tokenize
    strings = """\
1 + 2
3 + 4 * 6

1 and 5
(5 and 6) and 7

0
1

0x0
0x10
0xff
0xdeadbeef
0o0
0o56
0o755
0b0
0b1
0b11010101

1383
0123

0 + 0

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
    # these should not tokenize
    strings = """\
1.6
###
5and7
<=>
0xfg
0b00102
0o119
0a
0a0
0abc
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
