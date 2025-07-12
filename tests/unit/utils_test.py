import os
import re
from collections.abc import Callable
from pathlib import Path
from unittest.mock import patch

import pytest

from archlint.regexes import Regex
from archlint.utils import (
    Color,
    always_true,
    assert_bool,
    boolean_merge,
    compile_for_path_segment,
    compile_string_or_bool,
    dedup_underscores,
    deduplicate_ordered,
    default_module_name,
    default_module_root_dir,
    filter_with,
    filter_without,
    get_method_name,
    get_project_root,
    make_bar,
    make_colorize_path,
    make_double_bar,
    make_regex,
    move_path,
    path_matches,
    path_matches_not,
    prepend_module_name,
    remove_body,
    remove_ordering_index,
    safe_search,
    sort_on_path,
)


def test_get_project_root():
    PRIOR_PATH = Path.cwd()

    project_root = get_project_root()
    # assert project_root.name == "archlint"
    assert (project_root / "pyproject.toml").exists()
    assert (project_root / "tests").exists()
    assert (project_root / "src/archlint").exists()

    os.chdir(project_root / "tests" / "unit")
    new_project_root = get_project_root()
    assert new_project_root == project_root

    os.chdir(PRIOR_PATH)


def test_get_project_root__error():
    with patch.object(Path, "cwd", return_value=Path("/nonexistent")):
        with pytest.raises(
            FileNotFoundError,
            match="Directory root containing 'pyproject.toml' not found.",
        ):
            get_project_root()


def test_default_module_root_dir():
    assert default_module_root_dir() == Path("src/archlint")


def test_default_module_name():
    assert default_module_name() == "archlint"


@pytest.mark.parametrize(
    "to_move, old, new, expected",
    [
        (
            Path("/home/frodo/src/hello/utils.py"),
            Path("/home/frodo/src/hello"),
            Path("tests/unit"),
            Path("tests/unit/utils.py"),
        ),
        (
            Path("src/hello/utils.py"),
            Path("/home/frodo/src/hello"),
            Path("tests/unit"),
            Path("tests/unit/utils.py"),
        ),
        (
            Path("/home/frodo/src/hello/greeting_styles/rude.py"),
            Path("/home/frodo/src/hello"),
            Path("tests/unit"),
            Path("tests/unit/greeting_styles/rude.py"),
        ),
        (
            Path("src/hello/greeting_styles/rude.py"),
            Path("/home/frodo/src/hello"),
            Path("tests/unit"),
            Path("tests/unit/greeting_styles/rude.py"),
        ),
    ],
    ids=[0, 1, 2, 3],
)
def test_move_path(to_move: Path, old: Path, new: Path, expected: Path):
    assert move_path(to_move, old, new) == expected


def test_always_true():
    assert always_true("")
    assert always_true("a")
    assert always_true("Whatever, some longer string!")


def test_assert_bool():
    assert assert_bool(True) is True
    assert assert_bool(False) is False

    with pytest.raises(TypeError, match="Type 'bool' expected; found 'str'."):
        assert_bool("True")


def test_sort_on_path():
    pre = [
        "src/archlint/configuration.py:2:function_b",
        "src/archlint/configuration.py:1:function_a",
        "src/archlint/cli.py:3:ClassA.method3",
        "src/archlint/cli.py:2:ClassA.method2",
        "src/archlint/cli.py:1:ClassA.method1",
    ]
    post = [
        "src/archlint/cli.py:1:ClassA.method1",
        "src/archlint/cli.py:2:ClassA.method2",
        "src/archlint/cli.py:3:ClassA.method3",
        "src/archlint/configuration.py:1:function_a",
        "src/archlint/configuration.py:2:function_b",
    ]
    assert sort_on_path(pre) == post


@pytest.mark.parametrize(
    "incumbent, challenger, expected",
    [
        (
            {"a": False, "b": "string", "c": False},
            {"a": False, "b": True, "c": None},
            {"a": False, "b": True, "c": False},
        ),
        # (
        #     {},
        #     {},
        #     {},
        # ),
        # (
        #     {},
        #     {},
        #     {},
        # ),
    ],
)
def test_boolean_merge(incumbent: dict, challenger: dict, expected: dict):
    assert boolean_merge(incumbent, challenger) == expected


@pytest.mark.parametrize(
    "duplicated_list, expected",
    [
        ([], []),
        ([""], [""]),
        (["a", "a"], ["a"]),
        (["a", "c", "d", "c"], ["a", "c", "d"]),
        (["A", "a", "Z", "A", "Z"], ["A", "a", "Z"]),
    ],
)
def test_deduplicate_ordered(duplicated_list: list[str], expected: list[str]):
    deduplicated = deduplicate_ordered(duplicated_list)
    assert len(deduplicated) == len(set(duplicated_list))


@pytest.mark.parametrize(
    "unfiltered, criterion, expected",
    [
        ({"mod1", "mod2", "mod3"}, {"mod2"}, {"mod2"}),
        ({"mod1", "mod2", "mod3"}, "mod", {"mod1", "mod2", "mod3"}),
        ({"mod1", "mod2", "mod3"}, {"other"}, set()),
        ({"mod1", "mod2", "mod3"}, "mod1mod2mod3", set()),
        ({""}, "", {""}),
        ({"mod1", "mod2", "mod3"}, {"mod1", "mod2", "mod3"}, {"mod1", "mod2", "mod3"}),
    ],
)
def test_filter_with(unfiltered: set[str], criterion: str | set[str], expected: set[str]):
    assert filter_with(unfiltered, criterion) == expected


@pytest.mark.parametrize(
    "unfiltered, criterion, expected",
    [
        ({"mod1", "mod2", "mod3"}, {"mod2"}, {"mod1", "mod3"}),
        ({"mod1", "mod2", "mod3"}, "mod", set()),
        ({"mod1", "mod2", "mod3"}, {"other"}, {"mod1", "mod2", "mod3"}),
        ({"mod1", "mod2", "mod3"}, "mod1mod2mod3", {"mod1", "mod2", "mod3"}),
        ({"mod1", "mod2", "mod3"}, {"mod1", "mod2", "mod3"}, set()),
        ({""}, "", set()),
    ],
)
def test_filter_without(unfiltered: set[str], criterion: str | set[str], expected: set[str]):
    assert filter_without(unfiltered, criterion) == expected


@pytest.mark.parametrize(
    "pre, post",
    [
        ("/path/to/file.py:1:Class.method", "/path/to/file.py:Class.method"),
        ("/path/to/file.py:Class.method", "/path/to/file.py:Class.method"),
        ("file.py:456:Class.method", "file.py:Class.method"),
    ],
)
def test_remove_ordering_index(pre: str, post: str):
    assert remove_ordering_index(pre) == post


@pytest.mark.parametrize(
    "pre, module_name, post",
    [
        ("bar", "foo", "foo.bar"),
        ("foo.bar", "foo", "foo.bar"),
        ("bar.baz", "foo", "foo.bar.baz"),
    ],
)
def test_prepend_module_name(pre: str, module_name: str, post: str):
    assert prepend_module_name(pre, module_name) == post


@pytest.mark.parametrize(
    "pre, post",
    [
        ("don't change me", "don't change me"),
        ("dont_change_me", "dont_change_me"),
        ("change__me__", "change_me_"),
        ("change___me_-_too", "change_me_-_too"),
        ("__fix__me__", "_fix_me_"),
    ],
)
def test_dedup_underscores(pre: str, post: str):
    assert dedup_underscores(pre) == post


@pytest.mark.parametrize(
    "pre, post",
    [
        ("def method(self): ...", "def method(self)"),
        ("def method(self):\n        print(some_string)", "def method(self)"),
        (
            "def method(self) -> ReturnType: \n        print(some_string)",
            "def method(self) -> ReturnType",
        ),
    ],
)
def test_remove_body(pre: str, post: str):
    assert remove_body(pre) == post


@pytest.mark.parametrize(
    "pattern, to_search_in, group, result",
    [
        (re.compile(r"zz"), "abdominal", 0, ""),
        (re.compile(r"abdonimal"), "abdominal", 0, ""),
        (re.compile(r"ab+"), "abdominal", 0, "ab"),
        (re.compile(r"a(b+i)"), "stabbing", 0, "abbi"),
        (re.compile(r"/[^/]+?/"), "path/to/file", 0, "/to/"),
        (re.compile(r"/([^/]+?)/"), "path/to/second/file", 1, "to"),
        (re.compile(r"/([^/]+?)/([^/]+?)/"), "path/to/third/file", 2, "third"),
    ],
)
def test_safe_search(pattern: re.Pattern, to_search_in: str, group: int, result: str):
    assert safe_search(pattern, to_search_in, group) == result


@pytest.mark.parametrize(
    "uncompiled, compiled",
    [
        ("/[^/]+match_this.+", re.compile(r"/[^/]+match_this.+")),
        (r"match\.this", re.compile(r"match\.this")),
        ("match\\.this\\n", re.compile(r"match\.this\n")),
        (r"/[^/]+match\.this", re.compile(r"/[^/]+match\.this")),
        (r"match\.this\\n", re.compile(r"match\.this\n")),
        (r"match\\.this\\\\n", re.compile(r"match\.this\n")),
        (r"match\\(this\\n", re.compile(r"match\(this\n")),
    ],
    ids=[
        "no_backslash",
        "single_escape_raw",
        "double_escape",
        "single_escape_complex",
        "single_and_double_escaped",
        "double_and_quad_escaped",
        "double_escaped_paren",
    ],
)
def test_make_regex(uncompiled: str, compiled: re.Pattern):
    assert make_regex(uncompiled) == compiled


@pytest.mark.parametrize(
    "uncompiled, compiled",
    [
        ("/[^/]+match_this.+", re.compile(r"/[^/]+match_this.+")),
        ("match\\.this|match\\nthis\\n", re.compile(r"/[^/]*?match\.this|/[^/]*?match\nthis\n")),
        (
            ["match\\.this", "match\\nthis\\n"],
            re.compile(r"/[^/]*?match\.this|/[^/]*?match\nthis\n"),
        ),
        (
            [r"/[^/]+?match\.this", r"match\.this\n"],
            re.compile(r"/[^/]+?match\.this|/[^/]*?match\.this\n"),
        ),
        (r"/[^/]+match\.this|match\.this\n", re.compile(r"/[^/]+match\.this|/[^/]*?match\.this\n")),
    ],
    ids=["0", "1", "2", "3", "4"],
)
def test_compile_for_path_segment(uncompiled: str | list[str], compiled: re.Pattern):
    assert compile_for_path_segment(uncompiled) == compiled


@pytest.mark.parametrize(
    "string_or_bool, compiled",
    [
        (True, re.compile(".+")),
        (False, Regex.MATCH_NOTHING),
        ("/[^/]+match_this.+", re.compile(r"/[^/]+match_this.+")),
        ("/[^/]+match_this.+", re.compile(r"/[^/]+match_this.+")),
        (r"match\.this", re.compile(r"match\.this")),
        ("match\\.this\\n", re.compile(r"match\.this\n")),
        (r"/[^/]+match\.this", re.compile(r"/[^/]+match\.this")),
        (r"match\.this\\n", re.compile(r"match\.this\n")),
        (r"match\\.this\\\\n", re.compile(r"match\.this\n")),
        (r"match\\(this\\n", re.compile(r"match\(this\n")),
    ],
)
def test_compile_string_or_bool(string_or_bool: str | bool, compiled: re.Pattern):
    assert compile_string_or_bool(string_or_bool) == compiled


@pytest.mark.parametrize(
    "source, name",
    [
        ("def mymethod(): ...", "mymethod"),
        ("\n\n    def my_method(var1: str) -> str:\n", "my_method"),
        ("@abstractmethod\n    def parse_raw(", "parse_raw"),
        (
            "@property\n    @deal.has()\n    def _private_weird_method(self)",
            "_private_weird_method",
        ),
        ("def  no_match", ""),
        ("defnotamethod", ""),
    ],
)
def test_get_method_name(source: str, name: str):
    assert get_method_name(source) == name


@pytest.mark.parametrize(
    "path, pattern, success",
    [
        (
            Path("/tmp/hello-world/src/hello_world"),
            re.compile(r"/[^/]*?hello[^/]*?/|/[^/]*?other/[^/]*?/"),
            True,
        ),
        (
            Path("/tmp/hello-world/src/hello_world"),
            re.compile(r"src/hello[^/]*?"),
            True,
        ),
        (
            Path("/tmp/hello-world/src/hello_world"),
            re.compile(r"source/hello[^/]*?"),
            False,
        ),
    ],
)
def test_path_matches(path: Path, pattern: re.Pattern, success: bool):
    result = path_matches(path, pattern)
    if result:
        assert result in ({path} | set(path.parents))
    else:
        assert result is False


@pytest.mark.parametrize(
    "path, pattern, result",
    [
        (Path("/this/is/a/path"), re.compile(r"this_is_a_path"), True),
        (Path("this/is/a/path"), re.compile(r"/this/is"), True),
        (Path("this/is/a/path"), re.compile(r"a/path/"), True),
    ],
)
def test_path_matches_not(path: Path, pattern: re.Pattern, result: bool):
    assert path_matches_not(path, pattern) == result


class TestColor:
    colorizer = Color
    test_string = "WhaTeVer"

    def test_no_color(self):
        assert self.colorizer.no_color(self.test_string) == "WhaTeVer"

    def test_red(self):
        assert self.colorizer.red(self.test_string) == "\x1b[31mWhaTeVer\x1b[0m"

    def test_green(self):
        assert self.colorizer.green(self.test_string) == "\x1b[32mWhaTeVer\x1b[0m"

    def test_cyan(self):
        assert self.colorizer.cyan(self.test_string) == "\x1b[36mWhaTeVer\x1b[0m"

    def test_black(self):
        assert self.colorizer.black(self.test_string) == "\x1b[30mWhaTeVer\x1b[0m"

    def test_yellow(self):
        assert self.colorizer.yellow(self.test_string) == "\x1b[33mWhaTeVer\x1b[0m"

    def test_blue(self):
        assert self.colorizer.blue(self.test_string) == "\x1b[34mWhaTeVer\x1b[0m"

    def test_magenta(self):
        assert self.colorizer.magenta(self.test_string) == "\x1b[35mWhaTeVer\x1b[0m"

    def test_white(self):
        assert self.colorizer.white(self.test_string) == "\x1b[37mWhaTeVer\x1b[0m"


@pytest.mark.parametrize(
    "object_path_string, specific_path, root_dir, expected",
    [
        (
            "docs/md/checks.md:check_method_order",
            Path("docs/md"),
            Path("/home/johnny"),
            "docs/md/\x1b[36mchecks.md\x1b[0m:\x1b[31mcheck_method_order\x1b[0m",
        ),
        (
            "docs/md/checks.md:Methods.get_method_signature",
            Path("docs/md"),
            Path("/home/johnny"),
            "docs/md/\x1b[36mchecks.md\x1b[0m:\x1b[31mMethods.get_method_signature\x1b[0m",
        ),
        # ("", Path(""), Path(""), ""),
        # ("", Path(""), Path(""), ""),
        # ("", Path(""), Path(""), ""),
    ],
)
def test_make_colorize_path(
    object_path_string: str, specific_path: Path, root_dir: Path, expected: str
):
    colorize_path = make_colorize_path(specific_path, root_dir)
    assert colorize_path(object_path_string) == expected


@pytest.mark.parametrize(
    "message, colorizer, contained",
    [
        ("TEST TEXT", Color.red, "═TEST TEXT═"),
        (" some other text ", Color.red, "═ some other text ═"),
        # ("", Color.red, ""),
        # ("", Color.red, ""),
        # ("", Color.red, ""),
    ],
)
def test_make_double_bar(message: str, colorizer: Callable[[str], str], contained: str):
    assert contained in make_double_bar(message, colorizer)


@pytest.mark.parametrize(
    "message, colorizer, contained",
    [
        ("TEST TEXT", Color.red, "─TEST TEXT─"),
        (" some other text ", Color.red, "─ some other text ─"),
        # ("", Color.red, ""),
        # ("", Color.red, ""),
        # ("", Color.red, ""),
    ],
)
def test_make_bar(message: str, colorizer: Callable[[str], str], contained: str):
    assert contained in make_bar(message, colorizer)
