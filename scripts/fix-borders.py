#!/usr/bin/env python3
"""
fix-borders.py — Corrige l'ordre des bordures dans les DOCX générés par docx-js.
Le problème : docx-js génère parfois <w:bottom> avant <w:left> dans <w:pBdr>,
mais la spec OOXML exige l'ordre : top, left, bottom, right.

Usage: python fix-borders.py input.docx output.docx
"""

import sys
import os
import re
import subprocess

SCRIPTS_DIR = '/mnt/skills/public/docx/scripts/office'


def fix_borders(input_path, output_path=None):
    if output_path is None:
        output_path = input_path

    unpack_dir = '/tmp/fix-borders-unpacked'

    # Clean up
    if os.path.exists(unpack_dir):
        subprocess.run(['rm', '-rf', unpack_dir])

    # Unpack
    subprocess.run(
        ['python3', f'{SCRIPTS_DIR}/unpack.py', input_path, unpack_dir],
        capture_output=True, check=True
    )

    doc_path = os.path.join(unpack_dir, 'word', 'document.xml')
    with open(doc_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix border ordering in <w:pBdr> blocks
    # Pattern: find <w:pBdr> blocks where <w:bottom> comes before <w:left>
    def fix_pbdr(match):
        block = match.group(0)
        # Extract individual border elements
        borders = {}
        for tag in ['top', 'left', 'bottom', 'right']:
            pattern = rf'<w:{tag}[^/]*/>'
            m = re.search(pattern, block)
            if m:
                borders[tag] = m.group(0)

        if not borders:
            return block

        # Rebuild in correct order
        ordered = []
        for tag in ['top', 'left', 'bottom', 'right']:
            if tag in borders:
                ordered.append(borders[tag])

        # Get indentation from original
        indent_match = re.search(r'(\s+)<w:(top|left|bottom|right)', block)
        indent = indent_match.group(1) if indent_match else '\n          '

        new_borders = indent.join(ordered)
        result = re.sub(
            r'<w:(top|left|bottom|right)[^/]*/>\s*(?:<w:(top|left|bottom|right)[^/]*/>\s*)*',
            new_borders + '\n',
            block,
            count=1
        )
        return result

    # Apply fix to all <w:pBdr> blocks
    content = re.sub(r'<w:pBdr>.*?</w:pBdr>', fix_pbdr, content, flags=re.DOTALL)

    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(content)

    # Repack
    subprocess.run(
        ['python3', f'{SCRIPTS_DIR}/pack.py', unpack_dir, output_path, '--original', input_path],
        capture_output=True, check=True
    )

    # Cleanup
    subprocess.run(['rm', '-rf', unpack_dir])

    print(f"✅ Bordures corrigées : {output_path}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python fix-borders.py input.docx [output.docx]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else input_path
    fix_borders(input_path, output_path)
