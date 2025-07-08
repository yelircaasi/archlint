import re
from pathlib import Path

import grimp
import pytest

from archlint.configuration import (
    Configuration,
    DocsConfig,
    ImportInfo,
    ImportsConfig,
    MethodsConfig,
    TestsConfig,
)
from archlint.logic import (
    analyze_discrepancies,
    compute_disallowed,
    fix_dunder_filename,
    get_disallowed_imports,
    make_doc_class_path,
    make_doc_filename,
    make_doc_function_path,
    make_test_filename,
    make_test_function_path,
    make_test_method,
    make_test_method_path,
    map_to_doc,
    map_to_test,
    sort_methods,
)

cfg1 = (
    Configuration(
        root_dir=Path(""),
        module_name="",
        module_root_dir=Path(""),
        docs=DocsConfig(
            allow_additional=re.compile(r""),
            file_per_directory=re.compile(r""),
            file_per_class=re.compile(r""),
            ignore=re.compile(r""),
            replace_double_underscore=False,
            md_dir=Path(""),
        ),
        imports=ImportsConfig(
            internal_allowed_everywhere={""},
            external_allowed_everywhere={""},
            allowed=ImportInfo(internal={}, external={}),
            disallowed=ImportInfo(internal={}, external={}),
            grimp_cache="",
        ),
        methods=MethodsConfig(
            normal=9.0,
            ordering=(
                (re.compile(r""), 0.0),
                (re.compile(r""), 1.0),
            ),
        ),
        tests=TestsConfig(
            unit_dir=Path(""),
            allow_additional=re.compile(r""),
            ignore=re.compile(r""),
            file_per_class=re.compile(r""),
            file_per_directory=re.compile(r""),
            function_per_class=re.compile(r""),
            replace_double_underscore=False,
            use_filename_suffix=False,
        ),
    ),
)
cfg2 = (
    Configuration(
        root_dir=Path(""),
        module_name="",
        module_root_dir=Path(""),
        docs=DocsConfig(
            allow_additional=re.compile(r""),
            file_per_directory=re.compile(r""),
            file_per_class=re.compile(r""),
            ignore=re.compile(r""),
            replace_double_underscore=False,
            md_dir=Path(""),
        ),
        imports=ImportsConfig(
            internal_allowed_everywhere={""},
            external_allowed_everywhere={""},
            allowed=ImportInfo(internal={}, external={}),
            disallowed=ImportInfo(internal={}, external={}),
            grimp_cache="",
        ),
        methods=MethodsConfig(
            normal=9.0,
            ordering=(
                (re.compile(r""), 0.0),
                (re.compile(r""), 1.0),
            ),
        ),
        tests=TestsConfig(
            unit_dir=Path(""),
            allow_additional=re.compile(r""),
            ignore=re.compile(r""),
            file_per_class=re.compile(r""),
            file_per_directory=re.compile(r""),
            function_per_class=re.compile(r""),
            replace_double_underscore=False,
            use_filename_suffix=False,
        ),
    ),
)
icfg1 = ImportsConfig(
    internal_allowed_everywhere={""},
    external_allowed_everywhere={""},
    allowed=ImportInfo(internal={}, external={}),
    disallowed=ImportInfo(internal={}, external={}),
    grimp_cache="",
)
icfg2 = ImportsConfig(
    internal_allowed_everywhere={""},
    external_allowed_everywhere={""},
    allowed=ImportInfo(internal={}, external={}),
    disallowed=ImportInfo(internal={}, external={}),
    grimp_cache="",
)


@pytest.mark.parametrize(
    "config, pre, post",
    [
        (cfg1, "some_method", "test_some_method"),
        (cfg1, "__eq__", "test_dunder_eq"),
        (cfg2, "__le__", "test_dunder_le"),
    ],
)
def test_make_test_method(config: Configuration, pre: str, post: str):
    assert make_test_method(pre) == post


@pytest.mark.parametrize(
    "pre, post",
    [
        (Path("src/mymod/__init__.py"), Path("src/mymod/init.py")),
        (Path("src/mymod/__main__.py"), Path("src/mymod/main.py")),
        (Path("/home/ulysses/cool/src/cool/util.py"), Path("/home/ulysses/cool/src/cool/util.py")),
    ],
)
def test_fix_dunder_filename(pre: Path, post: Path):
    assert fix_dunder_filename(pre) == post


@pytest.mark.parametrize(
    "pre, use_suffix, post",
    [
        (
            Path("/home/ulysses/cool/src/cool/util.py"),
            True,
            Path("/home/ulysses/cool/src/cool/util_test.py"),
        ),
        (
            Path("/home/ulysses/cool/src/cool/util.py"),
            False,
            Path("/home/ulysses/cool/src/cool/test_util.py"),
        ),
        (Path("src/mymod/__init__.py"), True, Path("src/mymod/init_test.py")),
        (Path("src/mymod/__init__.py"), False, Path("src/mymod/test_init.py")),
        (Path("src/mymod/__main__.py"), True, Path("src/mymod/main_test.py")),
        (Path("src/mymod/__main__.py"), False, Path("src/mymod/test_main.py")),
    ],
)
def test_make_test_filename(pre: Path, use_suffix: bool, post: str):
    assert make_test_filename(pre, use_filename_suffix=use_suffix) == post


@pytest.mark.parametrize(
    "pre, post",
    [
        (Path("/home/ulysses/cool/src/cool/util.py"), Path("/home/ulysses/cool/src/cool/util.md")),
        (Path("src/mymod/__init__.py"), Path("src/mymod/init.md")),
        (Path("src/mymod/__main__.py"), Path("src/mymod/main.md")),
    ],
)
def test_make_doc_filename(pre: Path, post: Path):
    assert make_doc_filename(pre) == post


@pytest.mark.parametrize(
    "path, idx, class_name, method, file_per_class, file_per_directory, expected",
    [
        (
            Path("/some/path/to/file.py"),
            "1",
            "CoolClass",
            "cool_method",
            re.compile(r"some_string"),
            re.compile(r"some_string"),
            "/some/path/to/file_test.py:001:TestCoolClass.test_cool_method",
        ),
        (
            Path("/some/path/to/file.py"),
            "1",
            "CoolClass",
            "cool_method",
            re.compile(r"some_string"),
            re.compile(r"some_string"),
            "/some/path/to/file_test.py:001:TestCoolClass.test_cool_method",
        ),
        (
            Path("/some/path/to/file.py"),
            "1",
            "CoolClass",
            "cool_method",
            re.compile(r"some_string"),
            re.compile(r"some_string"),
            "/some/path/to/file_test.py:001:TestCoolClass.test_cool_method",
        ),
    ],
)
def test_make_test_method_path(
    path: Path,
    idx: str,
    class_name: str,
    method: str,
    file_per_class: re.Pattern,
    file_per_directory: re.Pattern,
    expected: str,
):
    result = make_test_method_path(
        path, idx, class_name, method, file_per_class, file_per_directory
    )
    assert result == expected


@pytest.mark.parametrize(
    "path, idx, klass, file_per_class, file_per_directory, expected",
    [
        (
            Path("some/path/to/file.py"),
            "1",
            "CoolClass",
            re.compile(r"some_string"),
            re.compile(r"some_string"),
            "some/path/to/file.md:001:CoolClass",
        ),
        (
            Path("/some/path/to/file.py"),
            "2",
            "CoolClass",
            re.compile(r"some_string"),
            re.compile(r"some_string"),
            "some/path/to/file.md:002:CoolClass",
        ),
        (
            Path("/some/path/to/file.py"),
            "42",
            "CoolClass",
            re.compile(r"some_string"),
            re.compile(r"some_string"),
            "some/path/to/file.md:034:CoolClass",
        ),
    ],
)
def test_make_doc_class_path(
    path: Path,
    idx: str,
    klass: str,
    file_per_class: re.Pattern,
    file_per_directory: re.Pattern,
    expected: str,
):
    result = make_doc_class_path(path, idx, klass, file_per_class, file_per_directory)
    assert result == expected


@pytest.mark.parametrize(
    "path, idx, func_name, file_per_directory, expected",
    [
        (Path(""), "", "", re.compile(r""), ""),
        (Path(""), "", "", re.compile(r""), ""),
        (Path(""), "", "", re.compile(r""), ""),
        (Path(""), "", "", re.compile(r""), ""),
    ],
)
def test_make_test_function_path(
    path: Path, idx: str, func_name: str, file_per_directory: re.Pattern, expected: str
):
    assert make_test_function_path(path, idx, func_name, file_per_directory) == expected


@pytest.mark.parametrize(
    "path, idx, func_name, file_per_directory, expected",
    [
        (Path(""), "", "", re.compile(r""), ""),
        (Path(""), "", "", re.compile(r""), ""),
        (Path(""), "", "", re.compile(r""), ""),
        (Path(""), "", "", re.compile(r""), ""),
    ],
)
def test_make_doc_function_path(
    path: Path, idx: str, func_name: str, file_per_directory: re.Pattern, expected: str
):
    assert make_doc_function_path(path, idx, func_name, file_per_directory) == expected


@pytest.mark.parametrize(
    "config, pre, post",
    [
        (cfg1, "", ""),
        (cfg1, "", ""),
        (cfg1, "", ""),
        (cfg1, "", ""),
    ],
)
def test_map_to_test(config: Configuration, pre: str, post: str):
    assert map_to_test(pre, config) == post


@pytest.mark.parametrize(
    "config, pre, post",
    [
        (cfg1, "", ""),
        (cfg2, "", ""),
        (cfg2, "", ""),
    ],
)
def test_map_to_doc(config: Configuration, pre: str, post: str):
    assert map_to_doc(pre, config) == post


@pytest.mark.parametrize(
    "allowed, disallowed, allowed_everywhere, graph, expected",
    [
        ({}, {}, {""}, "TODO", {}),
        ({}, {}, {""}, "TODO", {}),
        ({}, {}, {""}, "TODO", {}),
    ],
)
def test_compute_disallowed(
    allowed: dict[str, set[str]],
    disallowed: dict[str, set[str]],
    allowed_everywhere: set[str],
    graph: grimp.ImportGraph,
    expected: dict[str, set[str]],
):
    assert compute_disallowed(allowed, disallowed, allowed_everywhere, graph) == expected


@pytest.mark.parametrize(
    "config, pre, post",
    [
        (icfg1, "", ""),
        (icfg1, "", ""),
        (icfg2, "", ""),
        (icfg2, "", ""),
    ],
)
def test_get_disallowed_imports(config: ImportsConfig, pre: str, post: str):
    assert get_disallowed_imports(config, pre) == post


@pytest.mark.parametrize(
    "method_dict, post, methods_cfg",
    [
        (
            {"": ""},
            ["", ""],
            MethodsConfig(
                normal=6.66,
                ordering=(
                    (re.compile(r""), 0.0),
                    (re.compile(r""), 0.0),
                ),
            ),
        ),
        (
            {"": ""},
            ["", ""],
            MethodsConfig(
                normal=6.66,
                ordering=(
                    (re.compile(r""), 0.0),
                    (re.compile(r""), 0.0),
                ),
            ),
        ),
        (
            {"": ""},
            ["", ""],
            MethodsConfig(
                normal=6.66,
                ordering=(
                    (re.compile(r""), 0.0),
                    (re.compile(r""), 0.0),
                ),
            ),
        ),
    ],
)
def test_sort_methods(method_dict: dict[str, str], post: list[str], methods_cfg: MethodsConfig):
    assert sort_methods(method_dict, methods_cfg) == post


@pytest.mark.parametrize(
    "actual, expected, allow_additional, missing, unexpected, overlap",
    [
        (["", ""], ["", ""], re.compile(r""), ["", ""], ["", ""], {"", ""}),
        (["", ""], ["", ""], re.compile(r""), ["", ""], ["", ""], {"", ""}),
        (["", ""], ["", ""], re.compile(r""), ["", ""], ["", ""], {"", ""}),
    ],
)
def test_analyze_discrepancies(
    actual: list[str],
    expected: list[str],
    allow_additional: re.Pattern,
    missing: list[str],
    unexpected: list[str],
    overlap: set[str],
):
    result = analyze_discrepancies(actual, expected, allow_additional)
    assert result == (missing, unexpected, overlap)
