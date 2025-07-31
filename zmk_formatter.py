#!/usr/bin/env python3
"""ZMK Keymap Formatter - Aligns bindings blocks with consistent column widths."""

import re
import sys
from pathlib import Path


def print_info(message):
    """Print informational message with prefix."""
    print(f"[INFO] {message}")


def print_success(message):
    """Print success message with prefix."""
    print(f"[SUCCESS] {message}")


def print_warning(message):
    """Print warning message with prefix."""
    print(f"[WARNING] {message}")


def print_error(message):
    """Print error message with prefix."""
    print(f"[ERROR] {message}")


def parse_bindings_block(lines, start_idx):
    """Extract keycodes from a bindings block."""
    print_info(f"Parsing bindings block starting at line {start_idx + 1}")
    
    i = start_idx
    while i < len(lines) and not lines[i].strip().endswith('<'):
        i += 1
    i += 1
    
    content = ""
    brace_count = 1
    
    while i < len(lines) and brace_count > 0:
        line = lines[i].strip()
        brace_count += line.count('<') - line.count('>')
        line = re.sub(r'//.*$', '', line).strip()
        if line and not line.startswith('>;'):
            content += " " + line
        i += 1
    
    content = content.strip().rstrip('>;')
    keycodes = ['&' + part.strip() for part in content.split('&') if part.strip()]
    
    print_info(f"Found {len(keycodes)} keycodes in bindings block")
    if len(keycodes) < 42:
        print_warning(f"Block has only {len(keycodes)} keycodes, padding to 42")
    elif len(keycodes) > 42:
        print_warning(f"Block has {len(keycodes)} keycodes, may exceed expected grid size")
    
    return keycodes, i


def format_bindings_grid(keycodes):
    """Arrange keycodes into 4-row grid pattern."""
    print_info("Arranging keycodes into 4-row grid pattern")
    
    original_count = len(keycodes)
    while len(keycodes) < 42:
        keycodes.append('')
    
    if len(keycodes) > original_count:
        print_info(f"Padded grid with {len(keycodes) - original_count} empty cells")
    
    grid = []
    idx = 0
    
    # Rows 1-3: 6 + 2 blanks + tab + 2 blanks + 6
    for row_num in range(3):
        row = keycodes[idx:idx+6] + ['', '', 'TAB', '', ''] + keycodes[idx+6:idx+12]
        grid.append(row)
        idx += 12
        print_info(f"Created row {row_num + 1}: 6 + tab + 6 layout")
    
    # Row 4: 2 blanks + 6 + tab + 6 + 2 blanks
    row = ['', ''] + keycodes[idx:idx+6] + ['TAB'] + keycodes[idx+6:idx+12] + ['', '']
    grid.append(row)
    print_info("Created row 4: 2 blank + 6 + tab + 6 + 2 blank layout")
    
    return grid


def calculate_global_widths(all_grids):
    """Calculate max width for each column across all grids."""
    if not all_grids:
        print_warning("No grids found for width calculation")
        return []
    
    print_info(f"Calculating optimal column widths across {len(all_grids)} bindings block(s)")
    
    num_cols = len(all_grids[0][0])
    widths = []
    
    for col in range(num_cols):
        if col == 8:  # TAB column
            widths.append(0)
            continue
        
        max_width = 0
        for grid in all_grids:
            for row in grid:
                if col < len(row) and row[col] and row[col] != 'TAB':
                    max_width = max(max_width, len(row[col]))
        
        column_width = max_width + 1 if max_width > 0 else 1
        widths.append(column_width)
        print_info(f"Column {col + 1}: width = {column_width}")
    
    return widths


def format_grid_to_lines(grid, widths):
    """Convert grid to formatted lines."""
    print_info("Converting grid to formatted output lines")
    
    lines = []
    
    for row_idx, row in enumerate(grid):
        parts = []
        for col, cell in enumerate(row):
            if col == 8:  # Skip TAB marker
                continue
            elif col == 9:  # First column after tab
                content = cell if cell else ''
                parts.append('\t' + content.ljust(widths[col]))
            else:
                content = cell if cell else ''
                parts.append(content.ljust(widths[col]))
        
        formatted_line = ''.join(parts).rstrip()
        lines.append(formatted_line)
        print_info(f"Formatted grid row {row_idx + 1}")
    
    return lines


def format_zmk_file(file_path):
    """Format ZMK keymap file with aligned bindings blocks."""
    print_info(f"Starting to format ZMK keymap file: {file_path}")
    
    # Read file
    try:
        print_info("Reading input file...")
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        print_success(f"Successfully read {len(lines)} lines from file")
    except FileNotFoundError:
        print_error(f"File '{file_path}' not found")
        return False
    except PermissionError:
        print_error(f"Permission denied reading file '{file_path}'")
        return False
    except UnicodeDecodeError:
        print_error(f"Unable to decode file '{file_path}' as UTF-8")
        return False
    except Exception as e:
        print_error(f"Unexpected error reading file: {e}")
        return False
    
    # Collect all bindings blocks
    print_info("Scanning file for bindings blocks...")
    bindings_blocks = []
    all_grids = []
    i = 0
    block_count = 0
    
    while i < len(lines):
        if 'bindings =' in lines[i]:
            block_count += 1
            print_info(f"Found bindings block #{block_count} at line {i + 1}")
            
            try:
                keycodes, next_i = parse_bindings_block(lines, i)
                if keycodes:
                    grid = format_bindings_grid(keycodes)
                    bindings_blocks.append((i, next_i, lines[i].rstrip(), grid))
                    all_grids.append(grid)
                    print_success(f"Successfully processed bindings block #{block_count}")
                else:
                    print_warning(f"Bindings block #{block_count} contains no keycodes")
                i = next_i
            except Exception as e:
                print_error(f"Error processing bindings block #{block_count}: {e}")
                return False
        else:
            i += 1
    
    if not bindings_blocks:
        print_warning("No bindings blocks found in file")
        print_info("File appears to be valid but no formatting needed")
        return True
    
    print_success(f"Found and processed {len(bindings_blocks)} bindings block(s)")
    
    # Calculate global column widths
    print_info("Calculating global column alignment...")
    try:
        global_widths = calculate_global_widths(all_grids)
        print_success("Column width calculation complete")
    except Exception as e:
        print_error(f"Error calculating column widths: {e}")
        return False
    
    # Generate output
    print_info("Generating formatted output...")
    output_lines = []
    i = 0
    block_idx = 0
    
    try:
        while i < len(lines):
            if (block_idx < len(bindings_blocks) and 
                i == bindings_blocks[block_idx][0]):
                
                start_i, next_i, bindings_line, grid = bindings_blocks[block_idx]
                print_info(f"Formatting bindings block #{block_idx + 1}")
                
                output_lines.append(bindings_line)
                
                formatted_lines = format_grid_to_lines(grid, global_widths)
                output_lines.extend(line for line in formatted_lines if line.strip())
                output_lines.append('            >;')
                
                print_success(f"Formatted bindings block #{block_idx + 1}")
                block_idx += 1
                i = next_i
            else:
                output_lines.append(lines[i].rstrip())
                i += 1
        
        print_success("Output generation complete")
    except Exception as e:
        print_error(f"Error generating formatted output: {e}")
        return False
    
    # Write formatted file
    print_info("Writing formatted content to file...")
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines) + '\n')
        print_success(f"Successfully wrote formatted content to '{file_path}'")
        
        # Summary
        print("\n" + "="*60)
        print_success("FORMATTING COMPLETE")
        print(f"File: {file_path}")
        print(f"Bindings blocks processed: {len(bindings_blocks)}")
        print(f"Total lines: {len(output_lines)}")
        print("="*60)
        
        return True
    except PermissionError:
        print_error(f"Permission denied writing to file '{file_path}'")
        return False
    except Exception as e:
        print_error(f"Unexpected error writing file: {e}")
        return False


def main():
    print("ZMK Keymap Formatter")
    print("=" * 40)
    
    if len(sys.argv) != 2:
        print_error("Invalid number of arguments")
        print("Usage: python zmk_formatter.py <keymap_file>")
        print("\nExample:")
        print("  python zmk_formatter.py my_keymap.keymap")
        sys.exit(1)
    
    keymap_file = sys.argv[1]
    file_path = Path(keymap_file)
    
    print_info(f"Target file: {keymap_file}")
    
    # Validate file exists
    if not file_path.exists():
        print_error(f"File '{keymap_file}' does not exist")
        print_info("Please check the file path and try again")
        sys.exit(1)
    
    # Validate file is readable
    if not file_path.is_file():
        print_error(f"'{keymap_file}' is not a regular file")
        sys.exit(1)
    
    # Check if file appears to be a keymap file
    if not str(file_path).endswith(('.keymap', '.dtsi')):
        print_warning(f"File '{keymap_file}' doesn't have a typical ZMK extension (.keymap or .dtsi)")
        print_info("Proceeding anyway...")
    
    print_info(f"File size: {file_path.stat().st_size} bytes")
    
    # Process the file
    if not format_zmk_file(keymap_file):
        print_error("Formatting failed")
        sys.exit(1)


if __name__ == "__main__":
    main()