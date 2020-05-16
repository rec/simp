from argparse import Namespace
from pathlib import Path
from unittest import TestCase


def _simp():
    text = Path('simp').read_text()
    compiled = compile(text, 'simp', mode='exec')
    local = {}
    exec(compiled, local)
    return Namespace(**local)


simp = _simp()


class TestSimp(TestCase):
    def test_lines(self):
        actual = list(simp._process_lines(INPUT))
        for a in actual:
            print(a)
        expected = OUTPUT.splitlines()
        assert actual == expected

    def test_empty(self):
        assert list(simp._process_lines('')) == []
        assert list(simp._process_lines('\n')) == ['']
        assert list(simp._process_lines('\n\n')) == ['', '']


INPUT = """\
# something
# something else

from a import b
import foo
# comment goes ABOVE

from d import f
import foo.bar

# comment goes BELOW

END = 'here'
"""

OUTPUT = """\
# something
# something else

# comment goes ABOVE

from a import b
from d import f
import foo
import foo.bar

# comment goes BELOW

END = 'here'
"""
