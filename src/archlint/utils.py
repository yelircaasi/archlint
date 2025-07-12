"""
Small and simple utility functions.
"""

import re
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Literal

from archlint.regexes import Regex

# PATH -----------------------------------------------------------------------


def get_project_root() -> Path:
    _dir = Path.cwd()

    while not (_dir / "pyproject.toml").exists():
        _dir = _dir.parent

        if _dir == Path("/"):
            raise FileNotFoundError("Directory root containing 'pyproject.toml' not found.")

    return _dir


def default_module_root_dir() -> Path:
    cwd = Path.cwd()
    return next((cwd / "src").iterdir()).relative_to(cwd)


def default_module_name() -> str:
    return default_module_root_dir().name


def move_path(p: str | Path, old_base: Path, new_base: Path) -> Path:
    def join_on_common(path1: Path, path2: Path) -> Path | None:
        parts_base, parts_rel = path1.parts, path2.parts
        max_len = min(len(parts_base), len(parts_rel))
        for i in range(max_len):
            if parts_base[-i:] == parts_rel[:i]:
                return Path(*parts_base, *parts_rel[i:])
        return None

    if not (p := Path(p)).is_absolute():
        p = join_on_common(old_base, p) or p
    if p.is_relative_to(old_base):
        p = p.relative_to(old_base)
    elif p.is_absolute():
        raise ValueError(f"{p} should be relative to {old_base}, or at least overlap.")
    return new_base / p


# MISCELLANEOUS -------------------------------------------------------------


def always_true(s: str) -> bool:
    return True


def assert_bool(b: bool) -> bool:
    if not isinstance(b, bool):
        raise TypeError(f"Type 'bool' expected; found '{type(b).__name__}'.")
    return b


def sort_on_path(strings: Iterable[str]) -> list[str]:
    return sorted(strings, key=lambda s: s.rsplit(":", maxsplit=1)[0])


def boolean_merge(incumbent: dict, challenger: dict) -> dict:
    return {k: challenger.get(k) or incumbent.get(k) for k in set(incumbent) | set(challenger)}


# SEQUENCE PROCESSING --------------------------------------------------------


def deduplicate_ordered(strings: Iterable[str]) -> list[str]:
    new_list = []
    for s in strings:
        if s not in new_list:
            new_list.append(s)
    return new_list


def filter_with(string_set: set[str], contained: str | set[str]) -> set[str]:
    if isinstance(contained, str):
        return {s for s in string_set if contained in s}
    return {s for s in string_set if any(map(lambda c: c in s, contained))}


def filter_without(string_set: set[str], contained: str | set[str]) -> set[str]:
    if isinstance(contained, str):
        return {s for s in string_set if contained not in s}
    return {s for s in string_set if all(map(lambda c: c not in s, contained))}


# STRING PROCESSING ----------------------------------------------------------


def remove_ordering_index(s: str) -> str:
    return re.sub(r":\d+:", ":", s)


def prepend_module_name(s: str, module_name: str) -> str:
    if not s.startswith(module_name):
        return f"{module_name}.{s}"
    return s


def dedup_underscores(s: str) -> str:
    return re.sub("_+", "_", s)


def remove_body(s: str) -> str:
    return re.split(r": *\n|: *\.\.\. *\n?", s)[0]


# REGEX ----------------------------------------------------------------------


def safe_search(p: re.Pattern, s: str, groupnum: int, fallback: str = "") -> str:
    if srch := re.search(p, s):
        return srch.group(groupnum)
    return fallback


def make_regex(s: str) -> re.Pattern:
    s = re.sub(r"\\+", r"\\", s)
    return re.compile(s or r"(?!)")


def compile_for_path_segment(s: str | list[str]) -> re.Pattern:
    def preprocess(_s: str) -> str:
        if not _s.startswith("/"):
            return r"/[^/]*?" + _s
        return _s

    if not s:
        return Regex.MATCH_NOTHING

    segments = s.split("|") if isinstance(s, str) else s
    return make_regex("|".join(map(preprocess, segments)))


def compile_string_or_bool(s: str | bool) -> re.Pattern:
    s = str(s)
    if s == "True":
        return re.compile(".+")
    if s == "False":
        return Regex.MATCH_NOTHING
    return make_regex(s)


def get_method_name(s: str) -> str:
    return safe_search(Regex.METHOD_NAME, s, 1)


def path_matches(p: Path | str, path_pattern: re.Pattern) -> Path | Literal[False]:
    for parent in sorted((p := Path(p)).parents):
        if parent == Path("."):
            continue
        if re.search(path_pattern, str(parent)):
            return parent
    if re.search(path_pattern, str(p)):
        return p
    return False


def path_matches_not(p: Path | str, path_pattern: re.Pattern) -> bool:
    return not re.search(path_pattern, str(p))


# COLOR ----------------------------------------------------------------------


class Color:
    """
    Simple utility to add ANSI color codes to a string, including the reset at the end.
    """

    @staticmethod
    def no_color(s: str) -> str:
        return s

    @staticmethod
    def red(s: str) -> str:
        return f"\u001b[31m{s}\u001b[0m"

    @staticmethod
    def green(s: str) -> str:
        return f"\u001b[32m{s}\u001b[0m"

    @staticmethod
    def cyan(s: str) -> str:
        return f"\u001b[36m{s}\u001b[0m"

    @staticmethod
    def black(s: str) -> str:
        return f"\u001b[30m{s}\u001b[0m"

    @staticmethod
    def yellow(s: str) -> str:
        return f"\u001b[33m{s}\u001b[0m"

    @staticmethod
    def blue(s: str) -> str:
        return f"\u001b[34m{s}\u001b[0m"

    @staticmethod
    def magenta(s: str) -> str:
        return f"\u001b[35m{s}\u001b[0m"

    @staticmethod
    def white(s: str) -> str:
        return f"\u001b[37m{s}\u001b[0m"


def make_colorize_path(specific_dir: Path, root_dir: Path) -> Callable[[str], str]:
    # doc_prefix = f"{specific_dir.relative_to(root_dir)}/"
    # new_doc_prefix = f"{doc_prefix}\u001b[36m"
    doc_prefix = f"{specific_dir}/"
    new_doc_prefix = f"{doc_prefix}\u001b[36m"

    def colorize_path(s: str) -> str:
        new_colon = "\u001b[0m:\u001b[31m"
        s = remove_ordering_index(s)
        s = s.replace(doc_prefix, new_doc_prefix).replace(":", new_colon) + "\u001b[0m"
        return s

    return colorize_path


# DISPLAY --------------------------------------------------------------------


def make_double_bar(s: str = "", colorizer: Callable[[str], str] = Color.no_color) -> str:
    return colorizer(f"{s:═^80}")


def make_bar(s: str = "", colorizer: Callable[[str], str] = Color.no_color) -> str:
    return colorizer(f"{s:─^80}")
