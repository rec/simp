from unittest import TestCase
import simp


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
