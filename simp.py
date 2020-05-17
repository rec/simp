#!/usr/bin/env python3
"""
simp.py sorts Python imports simply.

"""
from pathlib import Path
import os
import sys
import argparse
import itertools
from myers import diff


def simp():
    args = _parse_args()
    all_files = list(_all_files(args.targets))
    changed_files = changed_lines = 0
    first = True

    for path in all_files:
        lines = path.read_text().splitlines()
        sorted_lines = _sort_imports(lines)
        if lines != sorted_lines:
            changed_files += 1

            mdiff = diff(lines, sorted_lines, context=2, format=True)
            delta = sum(i.startswith('+') for i in mdiff)

            changed_lines += delta
            if first:
                first = False
            else:
                print('', 50 * '-', '', sep='\n')

            print('%s: %s' % (path, _plural(delta, 'line')))

            if args.diff:
                print('', *mdiff, sep='\n')

            if args.execute:
                with open(path, 'w') as fp:
                    print(*sorted_lines, sep='\n', file=fp)

    if all_files:
        print()
    print('All files:', len(all_files))
    print('Imports out of order:')
    print('  Files:', changed_files)
    print('  Lines:', changed_lines)


def _plural(n, item, plural=None):
    if n != 1:
        item = plural if plural else item + 's'
    return '%d %s' % (n, item)


def _sort_imports(lines):
    def is_comment(s):
        s = s.strip()
        return not s or s.startswith('#')

    def is_import(s):
        return s.startswith('from ') or s.startswith('import ')

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
        arg = Path(arg)
        if arg.is_dir():
            yield from _one_tree(arg)
        elif arg.suffix in ('.py', ''):
            yield arg
        else:
            print('Do not understand file', arg, file=sys.stderr)


def _one_tree(root):
    root = Path(root)
    for directory, sub_dirs, files in os.walk(root):
        path = Path(directory)
        if path == root:
            sub_dirs[:] = (i for i in sub_dirs if i not in ('build', 'dist'))

        sub_dirs[:] = (i for i in sub_dirs if not i.startswith('.'))
        files[:] = (i for i in files if not i.startswith('.'))

        yield from (path / f for f in files if f.endswith('.py'))


def _parse_args(args=None):
    p = argparse.ArgumentParser(description=_DESCRIPTION)

    p.add_argument('targets', default=['.'], nargs='*', help=_TARGETS_HELP)
    p.add_argument('--diff', '-d', action='store_true', help=_DIFF_HELP)
    p.add_argument('--execute', '-x', action='store_true', help=_EXECUTE_HELP)

    return p.parse_args(args)


_DESCRIPTION = 'Sort the import directives in Python source files'

_DIFF_HELP = """If set, print diffs for each changed file"""

_TARGETS_HELP = """\
One or more Python files or directories with Python files.
Without arguments, runs simp on the current directory.
"""

_EXECUTE_HELP = """\
If set, actually make the changes to the Python files, otherwise just
list them."""


if __name__ == '__main__':
    simp()
