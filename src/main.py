"""Myers' diff (Assignment 1).

Usage:
    python3 main.py lines     A B   # Part A: minimal line diff of A -> B
    python3 main.py highlight A B   # Part B: the same diff plus changed-character ranges

The core is Eugene Myers' O(ND) algorithm in its linear-space form
("An O(ND) Difference Algorithm and Its Variations", 1986, section 4b):
find the middle snake of an optimal path with a forward and a backward
search running at the same time, then solve the two halves on either side
of it. Working this way needs only O(N + M) memory, which matters for the
500,000-line tests.
"""

import sys


# ---------------------------------------------------------------------------
# Reading input
# ---------------------------------------------------------------------------

def read_lines(path):
    """Read a file as raw bytes and split it into lines (problem statement, section 1).

    The content is split on b"\\n"; a trailing empty piece is dropped, so a
    final newline adds no extra line and an empty file has no lines. Any b"\\r"
    stays part of its line.
    """
    with open(path, "rb") as f:
        data = f.read()
    lines = data.split(b"\n")
    if lines[-1] == b"":
        lines.pop()
    return lines


# ---------------------------------------------------------------------------
# Myers' algorithm (linear-space variant)
# ---------------------------------------------------------------------------

def find_middle_snake(a, alo, ahi, b, blo, bhi, fv, bv):
    """Return a point (x, y) that lies on a shortest edit path of the box
    a[alo:ahi] x b[blo:bhi].

    Diagonals are numbered k = x - y using absolute coordinates.
    fv[k] is the furthest x reached on diagonal k by the forward search
    (from the top-left corner); bv[k] is the smallest x reached on diagonal k
    by the backward search (from the bottom-right corner). A negative k uses
    Python's negative indexing; the arrays are long enough that negative and
    positive diagonals never share a slot.
    Only diagonals inside the box (kmin..kmax) are ever explored, and the
    entries just outside the explored range are filled with sentinels, so the
    arrays can be shared between calls without being cleared.

    The caller has already removed the common prefix and suffix of the box,
    so the box is not empty in either direction and the edit distance D >= 2.
    The search therefore always stops with a point strictly inside an optimal
    path, and both halves around it have a smaller edit distance than D.
    """
    kmin = alo - bhi                 # lowest diagonal inside the box
    kmax = ahi - blo                 # highest diagonal inside the box
    fmid = alo - blo                 # diagonal of the top-left corner
    bmid = ahi - bhi                 # diagonal of the bottom-right corner
    odd = (fmid - bmid) & 1          # parity of delta = N - M

    fv[fmid] = alo
    bv[bmid] = ahi
    fmin = fmax = fmid               # diagonals covered by the forward search
    bmin = bmax = bmid               # diagonals covered by the backward search
    big = ahi + 1                    # sentinel for the backward array (> any x)

    while True:
        # ---- forward search: one more edit (d increases by one) ----
        if fmin > kmin:
            fmin -= 1
            fv[fmin - 1] = -1
        else:
            fmin += 1
        if fmax < kmax:
            fmax += 1
            fv[fmax + 1] = -1
        else:
            fmax -= 1
        for k in range(fmax, fmin - 1, -2):
            lo = fv[k - 1]           # x on diagonal k-1 (a step right gives lo + 1)
            hi = fv[k + 1]           # x on diagonal k+1 (a step down keeps x)
            x = hi if lo < hi else lo + 1
            y = x - k
            # follow the snake: diagonal moves over equal elements are free
            while x < ahi and y < bhi and a[x] == b[y]:
                x += 1
                y += 1
            fv[k] = x
        # The paths can only meet after a forward step when delta is odd.
        if odd:
            lo_k = bmin if bmin > fmin else fmin
            hi_k = bmax if bmax < fmax else fmax
            if (lo_k - fmin) & 1:
                lo_k += 1
            for k in range(lo_k, hi_k + 1, 2):
                if bv[k] <= fv[k]:
                    return fv[k], fv[k] - k

        # ---- backward search: one more edit ----
        if bmin > kmin:
            bmin -= 1
            bv[bmin - 1] = big
        else:
            bmin += 1
        if bmax < kmax:
            bmax += 1
            bv[bmax + 1] = big
        else:
            bmax -= 1
        for k in range(bmax, bmin - 1, -2):
            lo = bv[k - 1]           # x on diagonal k-1 (a step up keeps x)
            hi = bv[k + 1]           # x on diagonal k+1 (a step left gives hi - 1)
            x = lo if lo < hi else hi - 1
            y = x - k
            while x > alo and y > blo and a[x - 1] == b[y - 1]:
                x -= 1
                y -= 1
            bv[k] = x
        # The paths can only meet after a backward step when delta is even.
        if not odd:
            lo_k = bmin if bmin > fmin else fmin
            hi_k = bmax if bmax < fmax else fmax
            if (lo_k - bmin) & 1:
                lo_k += 1
            for k in range(lo_k, hi_k + 1, 2):
                if bv[k] <= fv[k]:
                    return bv[k], bv[k] - k


def myers_snakes(a, b):
    """Return the matched runs (x, y, length) of a shortest edit script turning
    a into b, sorted by position. a and b are sequences of comparable items."""
    n, m = len(a), len(b)
    # Diagonals run from -(m + 1) to n + 1 (including sentinels); n + m + 3
    # slots keep negative and non-negative indices apart.
    fv = [0] * (n + m + 3)
    bv = [0] * (n + m + 3)
    snakes = []

    # Explicit stack instead of recursion, so deep splits cannot overflow.
    stack = [(0, n, 0, m)]
    while stack:
        alo, ahi, blo, bhi = stack.pop()

        # Common prefix: a free snake at the start of the box.
        start = alo
        while alo < ahi and blo < bhi and a[alo] == b[blo]:
            alo += 1
            blo += 1
        if alo > start:
            snakes.append((start, blo - (alo - start), alo - start))

        # Common suffix: a free snake at the end of the box.
        end = ahi
        while ahi > alo and bhi > blo and a[ahi - 1] == b[bhi - 1]:
            ahi -= 1
            bhi -= 1
        if ahi < end:
            snakes.append((ahi, bhi, end - ahi))

        # Only deletions or only insertions are left: nothing to match.
        if alo == ahi or blo == bhi:
            continue

        x, y = find_middle_snake(a, alo, ahi, b, blo, bhi, fv, bv)
        stack.append((x, ahi, y, bhi))
        stack.append((alo, x, blo, y))

    snakes.sort()
    return snakes


def matching_pairs(a, b):
    """Return (ai, bi): parallel lists of indices such that a[ai[t]] == b[bi[t]]
    form a longest common subsequence of a and b, in increasing order."""
    ai = []
    bi = []
    for x, y, length in myers_snakes(a, b):
        ai.extend(range(x, x + length))
        bi.extend(range(y, y + length))
    return ai, bi


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def render(a, b):
    """Build the whole output as bytes.

    Between two consecutive kept lines all deleted lines are printed before
    all inserted lines, which is the delete-first rule."""
    ai, bi = matching_pairs(a, b)
    out = []
    emit = out.append
    i = j = 0
    ai.append(len(a))                # sentinel pair at the very end
    bi.append(len(b))
    last = len(ai) - 1
    for t in range(len(ai)):
        x, y = ai[t], bi[t]
        # change block: a[i:x] deleted, b[j:y] inserted
        for p in range(i, x):
            emit(b"-")
            emit(a[p])
            emit(b"\n")
        for q in range(j, y):
            emit(b"+")
            emit(b[q])
            emit(b"\n")
        if t == last:
            break
        emit(b" ")
        emit(a[x])
        emit(b"\n")
        i, j = x + 1, y + 1
    return b"".join(out)


def main() -> int:
    if len(sys.argv) != 4 or sys.argv[1] not in ("lines", "highlight"):
        print("usage: main.py lines|highlight A_PATH B_PATH", file=sys.stderr)
        return 2
    command, a_path, b_path = sys.argv[1:]
    try:
        a = read_lines(a_path)
        b = read_lines(b_path)
    except OSError as err:
        print("error: cannot read %s: %s" % (err.filename, err.strerror), file=sys.stderr)
        return 2
    sys.stdout.buffer.write(render(a, b))
    sys.stdout.buffer.flush()
    return 0


raise SystemExit(main())
