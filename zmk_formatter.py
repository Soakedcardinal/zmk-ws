#!/usr/bin/env python3
"""ZMK Keymap Formatter - Aligns bindings blocks with consistent column widths."""

import re
import sys
from pathlib import Path

def is_keymap_bindings(lines, i):
    """Check if bindings block is in keymap layer."""
    bc, in_keymap = 0, False
    for j in range(i, -1, -1):
        line = lines[j].strip()
        bc += line.count('}') - line.count('{')
        if bc > 0: break
        if re.search(r'^\s*\w+\s*\{', line):
            kbc = 0
            for k in range(j, -1, -1):
                kline = lines[k].strip()
                kbc += kline.count('}') - kline.count('{')
                if kbc > 0: break
                if 'keymap' in kline and '{' in kline:
                    in_keymap = True
                    break
            break
    return in_keymap

def parse_bindings(lines, start):
    """Extract keycodes from bindings block."""
    i = start
    while i < len(lines) and not lines[i].strip().endswith('<'): i += 1
    i += 1
    
    content, bc = "", 1
    while i < len(lines) and bc > 0:
        line = lines[i].strip()
        bc += line.count('<') - line.count('>')
        line = re.sub(r'//.*$', '', line).strip()
        if line and not line.startswith('>;'): content += " " + line
        i += 1
    
    keycodes = ['&' + p.strip() for p in content.strip().rstrip('>;').split('&') if p.strip()]
    return keycodes + [''] * (42 - len(keycodes)), i

def make_grid(keycodes):
    """Arrange into 4-row grid: 6+2+6, 6+2+6, 6+2+6, 2+6+6+2."""
    return [keycodes[i:i+6] + ['', ''] + keycodes[i+6:i+12] for i in range(0, 36, 12)] + \
           [['', ''] + keycodes[36:42] + keycodes[42:48] + ['', '']]

def calc_widths(grids):
    """Calculate max column widths."""
    return [max(len(row[c]) for g in grids for row in g if c < len(row) and row[c]) + 1 
            for c in range(len(grids[0][0]) if grids else 0)]

def format_grid(grid, widths):
    """Convert grid to formatted lines."""
    return [''.join(cell.ljust(widths[c]) if c != 8 else '\t' + cell.ljust(widths[c]) 
                   for c, cell in enumerate(row)).rstrip() for row in grid]

def format_zmk_file(file_path):
    """Format ZMK keymap file."""
    try:
        with open(file_path, 'r') as f: lines = f.readlines()
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    # Find keymap bindings blocks
    blocks, grids = [], []
    i = 0
    while i < len(lines):
        if 'bindings =' in lines[i] and is_keymap_bindings(lines, i):
            keycodes, next_i = parse_bindings(lines, i)
            grid = make_grid(keycodes)
            blocks.append((i, next_i, lines[i].rstrip(), grid))
            grids.append(grid)
            i = next_i
        else:
            i += 1
    
    if not blocks:
        print("No keymap bindings found")
        return True
    
    # Calculate global widths and format
    widths = calc_widths(grids)
    output, i, bi = [], 0, 0
    
    while i < len(lines):
        if bi < len(blocks) and i == blocks[bi][0]:
            start_i, next_i, bindings_line, grid = blocks[bi]
            output.append(bindings_line)
            output.extend(format_grid(grid, widths))
            output.append('            >;')
            bi += 1
            i = next_i
        else:
            output.append(lines[i].rstrip())
            i += 1
    
    try:
        with open(file_path, 'w') as f: f.write('\n'.join(output) + '\n')
        print(f"Formatted {len(blocks)} bindings blocks in {file_path}")
        return True
    except Exception as e:
        print(f"Error writing file: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python zmk_formatter.py <keymap_file>")
        sys.exit(1)
    
    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"File '{sys.argv[1]}' not found")
        sys.exit(1)
    
    if not format_zmk_file(sys.argv[1]):
        sys.exit(1)

if __name__ == "__main__":
    main()