from argparse import Namespace
from pathlib import Path
from unittest import TestCase
import diff


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


class TestDiff(TestCase):
    def test_diff(self):
        actual = diff.diff(INPUT.splitlines(), OUTPUT.splitlines())
        expected = DIFF.splitlines()
        assert actual == expected

    def test_short_diff(self):
        actual = diff.short_diff(INPUT.splitlines(), OUTPUT.splitlines())
        expected = SHORT_DIFF.splitlines()
        print(*actual, sep='\n')
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

DIFF = """\
 # something
 # something else

-from a import b
-import foo
 # comment goes ABOVE

+from a import b
 from d import f
+import foo
 import foo.bar

 # comment goes BELOW

 END = 'here'
"""

SHORT_DIFF = """\
 # something
 # something else

-from a import b
-import foo
 # comment goes ABOVE

+from a import b
 from d import f
+import foo
 import foo.bar

 # comment goes BELOW
[...17 lines skipped...]
"""
