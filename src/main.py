"""Myers' diff (Assignment 1).

Usage:
    python3 main.py lines     A B   # Part A: minimal line diff of A -> B
    python3 main.py highlight A B   # Part B: the same diff plus changed-character ranges
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
    # TODO: compute the diff and print it.
    return 0


raise SystemExit(main())
