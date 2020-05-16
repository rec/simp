import itertools

KEEP, INSERT, REMOVE = ' +-'


def myers_diff(a, b):
    # Adapted from
    # https://gist.github.com/adamnew123456/37923cf53f51d6b9af32a539cdfa7cc4
    front = {1: (0, [])}

    for d in range(0, len(a) + len(b) + 1):
        for k in range(-d, d + 1, 2):
            go_down = k == -d or (k != d and front[k - 1][0] < front[k + 1][0])

            if go_down:
                old_x, history = front[k + 1]
                x = old_x
            else:
                old_x, history = front[k - 1]
                x = old_x + 1

            history = history[:]
            y = x - k

            if 1 <= y <= len(b) and go_down:
                history.append((INSERT, b[y - 1]))
            elif 1 <= x <= len(a):
                history.append((REMOVE, a[x - 1]))

            while x < len(a) and y < len(b) and a[x] == b[y]:
                x += 1
                y += 1
                history.append((KEEP, a[x - 1]))

            if x >= len(a) and y >= len(b):
                return history
            front[k] = (x, history)

    raise ValueError('Could not find edit script')


def diff(a, b):
    diff = myers_diff(a, b)
    return [(a + b).rstrip() for (a, b) in diff]


def short_diff(a, b, frame=3):
    diff = myers_diff(a, b)

    def is_keep(a):
        return a[0] is KEEP

    def keepers(items):
        return list(itertools.takewhile(is_keep, items))

    prefix = keepers(diff)
    suffix = list(reversed(keepers(reversed(diff))))
    if len(prefix) + len(suffix) >= len(diff):
        return []

    begin = len(prefix) - frame
    end = -len(suffix) + frame

    lines = [(a + b).rstrip() for (a, b) in diff[begin:end]]

    def msg(n):
        return '[...%d line%s skipped...]' % (n, '' if n == 1 else 's')

    if begin > 0:
        lines.insert(0, msg(begin))
    e = len(diff) - end
    if e > 0:
        lines.append(msg(e))

    return lines
