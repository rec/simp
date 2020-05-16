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


def diff(a, b):
    diff = simp._myers_diff(a, b)
    return [(a + b).rstrip() for (a, b) in diff]


def sort_imports(text):
    return simp._sort_imports(text.splitlines())


class TestSimp(TestCase):
    def test_lines(self):
        actual = list(sort_imports(INPUT))
        for a in actual:
            print(a)
        expected = OUTPUT.splitlines()
        assert actual == expected

    def test_empty(self):
        assert list(sort_imports('')) == []
        assert list(sort_imports('\n')) == ['']
        assert list(sort_imports('\n\n')) == ['', '']


class TestDiff(TestCase):
    def test_diff(self):
        actual = diff(INPUT.splitlines(), OUTPUT.splitlines())
        expected = DIFF.splitlines()
        assert actual == expected

    def test_short_diff(self):
        actual = simp._short_diff(INPUT.splitlines(), OUTPUT.splitlines(), 3)
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
[...2 lines skipped...]
"""
