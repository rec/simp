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


def simp(targets, commit=False, diffs=False, execute=False, fail=False):
    if fail and (commit or execute):
        raise ValueError(
            '--fail is not compatible with either --commit or --execute'
        )

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
    first = True

    files = list(_all_files(targets))
    for path in files:
        with open(path) as fp:
            lines = fp.read().splitlines()
        sorted_lines = _sort_imports(lines)
        if lines != sorted_lines:
            disordered += 1
            if first:
                first = False
            elif diffs:
                print('', 50 * '-', '', sep='\n')

            if diffs:
                print(path + ':')
                mdiff = diff(lines, sorted_lines, context=2, format=True)
                print('', *mdiff, sep='\n')

            if not fail:
                print(path)

            if execute or commit:
                with open(path, 'w') as fp:
                    print(*sorted_lines, sep='\n', file=fp)

    if fail:
        return disordered

    if not disordered:
        print('All sorted')
        return

    if commit:
        cmd = 'git', 'commit', '-am', _MSG
        print()
        print(subprocess.check_output(cmd).decode('utf8'), end='')

    else:
        msg = '\n%d of %d Python file%s had unsorted includes'
        s = '' if len(files) == 1 else 's'
        print(msg % (disordered, len(files), s))


def _plural(n, item, plural=None):
    if n != 1:
        item = plural if plural else item + 's'
    return '%d %s' % (n, item)


def _sort_imports(lines):
    def is_comment(s):
        s = s.strip()
        return not s or s.startswith('#')

    def is_import(s):
        return s.startswith(('from ', 'import '))

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


def _parse_args(args=None):
    p = argparse.ArgumentParser(description=_DESCRIPTION)

    p.add_argument('targets', default=['.'], nargs='*', help=_TARGETS_HELP)
    p.add_argument('--commit', '-c', action='store_true', help=_COMMIT_HELP)
    p.add_argument('--diffs', '-d', action='store_true', help=_DIFFS_HELP)
    p.add_argument('--execute', '-x', action='store_true', help=_EXECUTE_HELP)
    p.add_argument('--fail', '-f', action='store_true', help=_FAIL_HELP)
    # p.add_argument('--quiet', '-f', action='store_true', help=_QUIET_HELP)

    return p.parse_args(args)


_DESCRIPTION = 'Sort the import directives in Python source files'

_DIFFS_HELP = """If set, print diffs for each changed file"""
_FAIL_HELP = """If set, the program fails if any changes need to be made"""
# _QUIET_HELP = """If set, the program fails if any changes need to be made"""

_TARGETS_HELP = """\
One or more Python files or directories with Python files.
Without arguments, runs simp on the current directory.
"""

_EXECUTE_HELP = """\
If set, actually make the changes to the Python files, otherwise just
list them."""

_COMMIT_HELP = """\
Make the changes and commit them.  Implies --execute
"""


if __name__ == '__main__':
    code = simp(**vars(_parse_args()))
    if code:
        sys.exit(code)
