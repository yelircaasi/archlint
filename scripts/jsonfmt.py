import json
import sys
from pathlib import Path

if sys.argv[1] in {"0", "1", "2", "3", "4", "5", "6", "7", "8"}:
    indent = int(sys.argv[1])
    paths = sys.argv[2:]
else:
    indent = 4
    paths = sys.argv[1:]
print(paths)
for fp in paths:
    file_path = Path(fp)
    d = json.loads(file_path.read_bytes())
    file_path.write_text(json.dumps(d, ensure_ascii=False, indent=indent))
