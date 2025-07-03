#!/usr/bin/env python

import os
import subprocess
import sys
from pathlib import Path


def first_newer(file1: str | Path, file2: str | Path) -> bool:
    m1 = os.path.getmtime(file1)
    m2 = os.path.getmtime(file2)
    return m1 > m2


def create_svg_if_necessary():
    viz_path = Path("codeqa/pydeps")
    index_path = viz_path / "pydeps.txt"
    git_head_path = Path(".git/logs/HEAD")

    assert index_path.exists(), index_path
    assert git_head_path.exists(), git_head_path

    if first_newer(git_head_path, index_path):
        orig_dir = Path(os.getcwd())
        os.chdir(viz_path)
        subprocess.run(["./run.sh"], check=False)
        os.chdir(orig_dir)
    else:
        print("pydeps visualizations are already more recent than the latest commit.")


if __name__ == "__main__":
    sys.exit(create_svg_if_necessary())
