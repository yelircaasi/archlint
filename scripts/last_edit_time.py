#!/usr/bin/env python

import sys
import time
from pathlib import Path


def most_recent_edit_time(directory: str | Path) -> str:
    FILTER_OUT = (".pyc",)
    FILTER_OUT_DIRS = ("__pycache__",)

    most_recent_time = 0.0

    for file_path in Path(directory).rglob("*"):
        if file_path.is_file() and str(file_path.parent) not in FILTER_OUT_DIRS:
            if not file_path.name.endswith(FILTER_OUT):
                mtime = file_path.stat().st_mtime
                most_recent_time = max(mtime, most_recent_time)

    time_modified: time.struct_time = time.strptime(time.ctime(most_recent_time))
    return time.strftime("%Y-%m-%d_%H:%M:%S", time_modified)


print(most_recent_edit_time(directory=sys.argv[1]))
