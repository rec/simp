#!/usr/bin/env python3
"""
simp.py sorts Python imports simply.

"""
from __future__ import print_function
from myers import diff
import argparse
import itertools
import os
import subprocess
import sys

_SUB = {'stderr': subprocess.DEVNULL, 'encoding': 'utf8'}
_MSG = 'Sort import statements with simp'
assert len(_MSG) <= 50


def simp(targets, commit=False, dry_run=True, fail=False):
    if dry_run:
        commit = False

    if commit:
        try:
            cmd = 'git', 'diff-index', '--quiet', 'HEAD', '--'
            subprocess.check_output(cmd)
        except subprocess.CalledProcessError:
            print(
                'simp --commit: Cannot commit with changes in the workspace',
                file=sys.stderr,
            )
            return 1

    disordered = 0
    for count, path in _all_files(targets):
        with open(path) as fp:
            lines = list(fp)

        sorted_lines = _sort_imports(lines)
        if lines == sorted_lines:
            continue

        if fail:
            return 1

        disordered += 1
        if dry_run:
            if count:
                print('', 50 * '-', '', sep='\n')

            print(path + ':')
            mdiff = diff(lines, sorted_lines, context=2, format=True)
            print('', *mdiff, sep='\n')

        print(path)
        if dry_run:
            continue

        with open(path, 'w') as fp:
            print(*sorted_lines, sep='\n', file=fp)

    if not disordered:
        print('All sorted')
        return

    if commit:
        cmd = 'git', 'commit', '-am', _MSG
        print()
        print(subprocess.check_output(cmd).decode(), end='')

    else:
        msg = '\n%d of %d Python file%s had unsorted includes'
        s = '' if count == 1 else 's'
        print(msg % (disordered, count, s))


def _plural(n, item, plural=None):
    if n != 1:
        item = plural if plural else item + 's'
    return '%d %s' % (n, item)


def _sort_imports(lines):
    def is_comment(s):
        s = s.strip()
        return not s or s.startswith('#')

    def is_import(s):
        return s.startswith(('from ', 'import ')) and '__future__' not in s

    def still_import(s):
        return is_import(s) or is_comment(s)

    before = list(itertools.takewhile((lambda s: not is_import(s)), lines))
    lines = lines[len(before) :]

    imports = list(itertools.takewhile(still_import, lines))
    after = lines[len(imports) :]

    while imports and is_comment(imports[-1]):
        after.insert(0, imports.pop())

    comments = [s for s in imports if is_comment(s)]
    imports = [s for s in imports if not is_comment(s)]

    return before + comments + sorted(set(imports)) + after


def _all_files(args):
    for arg in args:
        if os.path.isdir(arg):
            for i in _one_tree(arg):
                yield i
        elif arg.endswith('.py') or '.' not in arg:
            yield arg
        else:
            print('Do not understand file', arg, file=sys.stderr)


def _one_tree(root):
    for directory, sub_dirs, files in os.walk(root):
        if directory == root:
            sub_dirs[:] = (i for i in sub_dirs if i not in ('build', 'dist'))

        sub_dirs[:] = (i for i in sub_dirs if not i.startswith('.'))
        files[:] = (i for i in files if not i.startswith('.'))

        for f in files:
            if f.endswith('.py'):
                yield os.path.join(directory, f)


def parser():
    p = argparse.ArgumentParser(description=_DESCRIPTION, epilog=_EPILOG)

    p.add_argument('targets', default=['.'], nargs='*', help=_TARGETS_HELP)
    p.add_argument('--commit', '-c', action='store_true', help=_COMMIT_HELP)
    p.add_argument('--dry_run', '-d', action='store_true', help=_DRY_RUN_HELP)
    p.add_argument('--fail', '-f', action='store_true', help=_FAIL_HELP)

    return p


def parse_args(args=None):
    return parser().parse_args(args)


_DESCRIPTION = """
Sort imports in Python files, leaving ``from __future__`` imports at the top.
"""

_EPILOG = """I wanted to sort my Python includes with no fuss.  ``simp`` finds
the first block of unindented import statements, and sorts them.  Any comments
between import lines bubble up to the top in their original order."""

_FAIL_HELP = """If set, the program fails if any changes need to be made.
This is useful for a commit hook to check if all imports are sorted."""

_TARGETS_HELP = """\
One or more Python files or directories with Python files.
Without arguments, runs simp on the current directory.
"""

_DRY_RUN_HELP = """\
If set, do not make the changes to the Python files, but just
list the diffs."""

_COMMIT_HELP = 'Git commit the changes'


if __name__ == '__main__':
    code = simp(**vars(parse_args()))
    if code:
        sys.exit(code)
