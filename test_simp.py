from unittest import TestCase
from pathlib import Path

_SIMP = {}


def _simp():
    if not _SIMP:
        text = Path('simp').read_text()
        compiled = compile(text, 'simp', mode='exec')
        exec(compiled, _SIMP)
    return _SIMP


class TestSimp(TestCase):
    def test_lines(self):
        actual = list(_simp()['_process_lines'](INPUT))
        for a in actual:
            print(a)
        expected = OUTPUT.splitlines()
        assert actual == expected


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
