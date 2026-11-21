#!/usr/bin/env python3
"""Entry program: copy the code-drawn passport spread to /output/entry.png.

Stdlib only. Deterministic: the same bytes are written on every run.
The spread itself is drawn by draw_passport.py (Pillow, run locally at
build time); this program only copies the committed entry.png.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SRC, dst)
    os.chmod(dst, 0o644)
    print("wrote", dst, os.path.getsize(dst), "bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
