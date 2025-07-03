#!/usr/bin/env python

import json
import os
import subprocess
import sys
from pathlib import Path


def first_newer(file1: str | Path, file2: str | Path) -> bool:
    m1 = os.path.getmtime(file1)
    m2 = os.path.getmtime(file2)
    return m1 > m2


def write_sbom_if_necessary():
    sbom_path = Path("sbom.json")
    lock_path = Path("poetry.lock")

    assert sbom_path.exists() and lock_path.exists()

    if first_newer(lock_path, sbom_path):
        result = subprocess.run(["cyclonedx-py", "poetry"], stdout=subprocess.PIPE, check=False)
        output = json.loads(result.stdout.decode())
        with open(sbom_path, "w") as f:
            json.dump(output, f, indent=2)
        print("Wrote sbom.json.")
    else:
        print("sbom.json is already more recent than poetry.lock")


if __name__ == "__main__":
    sys.exit(write_sbom_if_necessary())
