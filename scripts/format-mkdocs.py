import re
import subprocess
import sys
from collections.abc import Iterable
from pathlib import Path
from random import choices
from string import ascii_letters

indented_yaml: re.Pattern = re.compile(r"::: .+?(?=\n[^ ])|::: .+?(?=\n$)", re.DOTALL)


def get_files(file_list: Iterable[str | Path]) -> list[Path]:
    files = []
    for file_path in file_list:
        if (p := Path(file_path)).is_file():
            if str(file_path).endswith(".md"):
                files.append(p)
        elif p.is_dir():
            files.extend(get_files(p.iterdir()))
    return files


def random_string() -> str:
    return "".join(choices(ascii_letters, k=20)).title()


def alias_yaml(file_list: list[Path]) -> dict[str, str]:
    aliases = {}
    for file_path in file_list:
        md_text = Path(file_path).read_text()
        for yaml_block in re.findall(indented_yaml, md_text):
            if yaml_block not in aliases:
                aliases.update({yaml_block: random_string()})
        for yaml_block, alias in aliases.items():
            md_text = md_text.replace(yaml_block, alias)
        file_path.write_text(md_text)
    return aliases


def dealias_yaml(file_list: list[Path], alias_dict: dict[str, str]) -> None:
    for file_path in file_list:
        md_text = file_path.read_text()
        for yaml_block, alias in alias_dict.items():
            md_text = md_text.replace(alias, yaml_block)
        file_path.write_text(md_text)


def format(file_list: list[Path]) -> None:
    options = [
        "--extensions",
        "mkdocs",
        "--number",
        "--no-codeformatters",
        "--align-semantic-breaks-in-lists",
        "--ignore-missing-references",
    ]
    aliases = alias_yaml(file_list)
    subprocess.run(["mdformat", *options, *map(str, file_list)], check=False)
    dealias_yaml(file_list, aliases)


if __name__ == "__main__":
    files = get_files(sys.argv[1:])
    print(files)
    format(files)
    sys.exit(0)
