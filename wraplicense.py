#!/usr/bin/env python3
"""
wraplicense.py — reflow a license text file to a fixed width, computing
each paragraph's hanging (continuation-line) indent from its own tag
length, so "a. " (3 chars) and "    a. " (7 chars) and "10. " (4 chars)
all get correctly aligned continuation lines instead of one hardcoded
indent for the whole document.

Usage:
    python3 wraplicense.py INPUT.txt > OUTPUT.txt
    python3 wraplicense.py -w 72 INPUT.txt > OUTPUT.txt
"""

import argparse
import re
import sys
import textwrap

# Matches a leading tag: optional whitespace, then either
#   - a letter or number followed by ". " (e.g. "a. ", "10. ")
# Captures the whole tag (including its own leading indent) so we know
# exactly how many columns of hang the continuation lines need.
TAG_RE = re.compile(r'^(\s*(?:[a-zA-Z]|\d+)\.\s+)')

# Lines we never want to touch by rewrapping — the license header block
# (title / copyright / permission notice) is conventionally kept as
# separate hard lines, not reflowed prose. Detect this as "the first
# paragraph of the file" and pass it through untouched.
def is_header_paragraph(para_lines, para_index):
    return para_index == 0


def split_paragraphs(text):
    """Split on blank lines, keeping track of raw paragraph blocks."""
    raw_paras = re.split(r'\n\s*\n', text.strip('\n'))
    return [p for p in raw_paras]


def rewrap_paragraph(para, width):
    lines = para.split('\n')
    first_line = lines[0]

    m = TAG_RE.match(first_line)
    if m:
        tag = m.group(1)
        initial_indent = tag
        subsequent_indent = ' ' * len(tag)
        # Strip the tag off the first line before rejoining — otherwise
        # it gets duplicated when initial_indent is prepended below.
        first_line = first_line[m.end():]
        lines = [first_line] + lines[1:]
    else:
        initial_indent = ''
        subsequent_indent = ''

    # Collapse the paragraph's existing line breaks + indentation into
    # one continuous string of words before rewrapping.
    joined = ' '.join(line.strip() for line in lines)
    # Also collapse any accidental double-spaces from prior manual edits.
    joined = re.sub(r' {2,}', ' ', joined).strip()

    wrapped = textwrap.fill(
        joined,
        width=width,
        initial_indent=initial_indent,
        subsequent_indent=subsequent_indent,
        break_long_words=False,
        break_on_hyphens=False,
    )
    return wrapped


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('infile', help='input license text file')
    ap.add_argument('-w', '--width', type=int, default=72,
                     help='max line width (default: 72)')
    args = ap.parse_args()

    with open(args.infile, 'r', encoding='utf-8') as f:
        text = f.read()

    paragraphs = split_paragraphs(text)
    out_paras = []
    for i, para in enumerate(paragraphs):
        if is_header_paragraph(paragraphs, i):
            # Pass the header block through as-is, line by line,
            # but still collapse stray double-spaces on each line.
            fixed_lines = [re.sub(r' {2,}', ' ', ln) for ln in para.split('\n')]
            out_paras.append('\n'.join(fixed_lines))
            continue
        out_paras.append(rewrap_paragraph(para, args.width))

    result = '\n\n'.join(out_paras) + '\n'
    sys.stdout.write(result)


if __name__ == '__main__':
    main()
