#!/usr/bin/env python3
# Author: Tim Harrison
# Created: 2026-09-26
# Updated: 2026-10-11

"""Package the world into an installable .apworld.

A zip with the world package at its root. Respects per-directory .apignore
files; __pycache__, .pyc, and previous .apworld artifacts never ship.

Usage: package_apworld.py <output.apworld> <world_package_name>
Used by `make package` (world/Makefile) and mirrored in the CI smoke test.
"""
import os
import sys
import zipfile
import fnmatch

# Dev-only files maintained in the repo but never shipped in the .apworld.
NON_SHIP_FILES = {'.gitignore', '.apignore', '.git', '.gitmodules', 'ruff.toml', 'README.md'}
NON_SHIP_DIRS = {'.github', 'scripts', '__pycache__', '.ruff_cache'}


def main() -> None:
    out, world_name = sys.argv[1], sys.argv[2]

    ignore_patterns = []
    for root, _dirs, _files in os.walk('.'):
        ap = os.path.join(root, '.apignore')
        if os.path.isfile(ap):
            with open(ap) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        ignore_patterns.append(os.path.join(root, line))

    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs
                       if d not in NON_SHIP_DIRS and d != '.git']
            for f in files:
                p = os.path.join(root, f)
                if p == out or f in NON_SHIP_FILES or p.endswith('.pyc'):
                    continue
                if any(fnmatch.fnmatch(p, pat) or p.startswith(pat.rstrip('/'))
                       for pat in ignore_patterns):
                    continue
                z.write(p, os.path.join(world_name, os.path.relpath(p, '.')))

    with zipfile.ZipFile(out) as z:
        assert z.testzip() is None, 'corrupt member'
        names = z.namelist()
        assert not any(n.endswith('.pyc') for n in names), 'pyc leaked into apworld'
        assert any(n.endswith('__init__.py') for n in names), 'world sources missing'
        leaks = [n for n in names if any(s in n for s in ('.ruff_cache', 'ruff.toml', 'README'))]
        assert not leaks, f'dev files leaked into apworld: {leaks}'
        print(f'packaged {out}: {len(names)} files')


if __name__ == '__main__':
    main()