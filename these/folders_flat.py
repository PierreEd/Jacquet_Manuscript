#!/usr/bin/env python3
"""
Flatten *_png folders:
- Find all directories named like <something>_png under a root folder
- Move (or copy) all PNGs from each *_png folder into its parent directory
  e.g. Chap1/figure_png/figure_p001.png  ->  Chap1/figure_p001.png

Usage (Windows CMD / PowerShell):
  python flatten_png_folders.py "C:\path\to\these"

Notes:
- Set MOVE_FILES = False to copy instead of move
- Set DELETE_EMPTY_FOLDERS = True to remove *_png folders after processing
"""

from __future__ import annotations
from pathlib import Path
import shutil

MOVE_FILES = True            # True = move, False = copy
DELETE_EMPTY_FOLDERS = False # True = delete *_png folders if empty after move/copy


def unique_dest(dest: Path) -> Path:
    """If dest exists, append _001, _002, ... before suffix."""
    if not dest.exists():
        return dest
    stem, suffix = dest.stem, dest.suffix
    parent = dest.parent
    k = 1
    while True:
        candidate = parent / f"{stem}_{k:03d}{suffix}"
        if not candidate.exists():
            return candidate
        k += 1


def flatten_one_folder(png_folder: Path) -> tuple[int, int]:
    """
    Move/copy all .png files directly inside png_folder to its parent.
    Returns (n_moved_or_copied, n_skipped).
    """
    parent_dir = png_folder.parent
    n_done = 0
    n_skipped = 0

    # Only take PNGs directly in the folder (not nested); change to rglob if needed.
    for png in sorted(png_folder.glob("*.png")):
        dest = unique_dest(parent_dir / png.name)

        try:
            if MOVE_FILES:
                shutil.move(str(png), str(dest))
            else:
                shutil.copy2(str(png), str(dest))
            n_done += 1
        except Exception:
            n_skipped += 1

    # Optionally delete folder if empty
    if DELETE_EMPTY_FOLDERS and MOVE_FILES:
        try:
            # remove only if empty
            next(png_folder.iterdir())
        except StopIteration:
            png_folder.rmdir()

    return n_done, n_skipped


def main(root: Path) -> None:
    root = root.expanduser()
    if not root.exists():
        raise SystemExit(f"Error: root path does not exist: {root}")

    png_folders = [p for p in root.rglob("*") if p.is_dir() and p.name.lower().endswith("_png")]
    if not png_folders:
        print(f"No *_png folders found under: {root}")
        return

    total_done = 0
    total_skipped = 0

    for folder in sorted(png_folders):
        done, skipped = flatten_one_folder(folder)
        if done or skipped:
            print(f"{folder} -> parent {folder.parent} | moved/copied: {done}, skipped: {skipped}")
        total_done += done
        total_skipped += skipped

    print(f"\nDone. Total moved/copied: {total_done}, skipped: {total_skipped}")


if __name__ == "__main__":
    import sys
    arg = sys.argv[1] if len(sys.argv) > 1 else "."
    # Make it robust to accidental quotes
    arg = arg.strip().strip('"').strip("'")
    main(Path(arg).absolute())
