import re
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any, Literal, TypeVar

from archlint.regexes import Regex

# PATH -----------------------------------------------------------------------


def get_project_root() -> Path:
    attempts, max_attempts = 0, 20
    _dir = Path.cwd()

    while not (_dir / "pyproject.toml").exists():
        _dir = (Path(__file__) if _dir == Path("/") else _dir).parent

        if (attempts := attempts + 1) > max_attempts:
            raise FileNotFoundError("Directory root containing 'pyproject.toml' not found.")

    return _dir


def walk_absolute_paths():
    directory = Path("src/datethyme/").resolve()
    for path in directory.rglob("*.py"):
        yield path.resolve()


def move_path(p: str | Path, old_base: Path, new_base: Path, root: Path) -> Path:
    return (new_base / (Path(p).relative_to(old_base))).relative_to(root)


def relativize(p: str | Path, root_dir: Path) -> Path:
    return move_path(p, root_dir, root_dir, root_dir)


# MISCELLANEOUS -------------------------------------------------------------


def always_true(s: str) -> bool:
    return True


def assert_bool(b: bool) -> bool:
    if not isinstance(b, bool):
        raise TypeError(f"Type 'bool' expected; found '{type(b)}'.")
    return b


T = TypeVar("T")
U = TypeVar("U")


def project(single: Any, _list: list[tuple] | list[str]) -> list[tuple]:
    return [(single, *elem) if isinstance(elem, tuple) else (single, elem) for elem in _list]


def sort_on_path(strings: Iterable[str]) -> list[str]:
    return sorted(strings, key=lambda s: s.split(":")[0])


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


def anywhere(sset: set[str], substring: str) -> bool:
    return bool(filter_with(sset, substring))


# STRING PROCESSING ----------------------------------------------------------


def prepend_module_name(s: str, module_name: str) -> str:
    if not s.startswith(module_name):
        return f"{module_name}.{s}"
    return s


def dedup_underscores(s: str) -> str:
    return re.sub("_+", "_", s)


def remove_body(s: str) -> str:
    return re.split(r": *\n|: *\.\.\. *\n", s)[0]


# REGEX ----------------------------------------------------------------------


def safe_search(p: re.Pattern, s: str, groupnum: int, fallback: str = "") -> str:
    if srch := re.search(p, s):
        return srch.group(groupnum)
    return fallback


def make_regex(s: str) -> re.Pattern:
    return re.compile(re.sub(r"\\*\(", "\\(", re.sub(r"\\*\.", "\\.", s)))


def compile_for_path_segment(s: str) -> re.Pattern:
    if not s:
        return Regex.MATCH_NOTHING
    segments = [f"/[^/]*?{seg}[^/]*?" for seg in s.replace(".", "\\.").split("|")]
    return re.compile(re.sub(r"\\+\.", "\\.", "|".join(segments)))


def compile_for_path_segment_or_bool(s: str | bool) -> re.Pattern:
    s = str(s)
    if s == "True":
        return re.compile(".")
    if s == "False":
        return compile_for_path_segment("")
    return compile_for_path_segment(s)


def get_method_name(s: str) -> str:
    return safe_search(Regex.NAME_PATTERN, s, 1)


def path_matches(p: Path | str, path_pattern: re.Pattern) -> Path | Literal[False]:
    if s := re.search(path_pattern, p := str(p)):
        dirname = s.group(0)[1:]
        return Path(p.split(dirname)[0]) / dirname
    return False


def path_matches_not(p: Path | str, path_pattern: re.Pattern) -> bool:
    return not path_matches(p, path_pattern)


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
    def cyan(s: str) -> str:
        return f"\u001b[36m{s}\u001b[0m"

    @staticmethod
    def white(s: str) -> str:
        return f"\u001b[37m{s}\u001b[0m"


def make_colorize_path(specific_dir: Path, root_dir: Path) -> Callable[[str], str]:
    doc_prefix = f"{specific_dir.relative_to(root_dir)}/"
    new_doc_prefix = f"{doc_prefix}\u001b[36m"

    def colorize_path(s: str) -> str:
        new_colon = "\u001b[0m:\u001b[31m"
        s = s.replace(doc_prefix, new_doc_prefix).replace(":", new_colon) + "\u001b[0m"
        return s

    return colorize_path


# DISPLAY --------------------------------------------------------------------


def make_double_bar(s: str = "", colorizer: Callable[[str], str] = Color.no_color) -> str:
    return colorizer(f"{s:═^80}")


def make_bar(s: str = "", colorizer: Callable[[str], str] = Color.no_color) -> str:
    return colorizer(f"{s:─^80}")


def make_half_bar(s: str = "", colorizer: Callable[[str], str] = Color.no_color) -> str:
    return colorizer(f"\n{Color.cyan(s) + ' ':-<85}")


def indented(strings: Iterable[str], colorizer: Callable[[str], str] = Color.no_color) -> str:
    return "    " + "\n    ".join(sorted(map(colorizer, strings)))
