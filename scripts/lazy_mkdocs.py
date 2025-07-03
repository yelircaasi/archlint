#!/usr/bin/env python

import os
import subprocess
import sys
from pathlib import Path


def first_newer(file1: str | Path, file2: str | Path) -> bool:
    m1 = os.path.getmtime(file1)
    m2 = os.path.getmtime(file2)
    return m1 > m2


def build_docs_if_necessary():
    mkdocs_path = Path("docs/md")
    index_path = Path("docs/site/index.html")
    git_head_path = Path(".git/logs/HEAD")

    assert index_path.exists(), index_path
    assert git_head_path.exists(), git_head_path

    if first_newer(git_head_path, index_path):
        orig_dir = Path(os.getcwd())
        os.chdir(mkdocs_path)
        subprocess.run(["mkdocs", "build"], check=False)
        os.chdir(orig_dir)
    else:
        print("mkdocs build is already more recent than the latest commit.")


if __name__ == "__main__":
    sys.exit(build_docs_if_necessary())
