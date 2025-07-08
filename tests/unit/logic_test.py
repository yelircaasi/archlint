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
    TstsConfig,
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

int_graph = grimp.build_graph(
    "archlint",
    include_external_packages=False,
    cache_dir="/tmp/grimp_cache",
)
ext_graph = grimp.build_graph(
    "archlint",
    include_external_packages=True,
    cache_dir="/tmp/grimp_cache",
)
icfg1 = ImportsConfig(
        internal_allowed_everywhere={""},
        external_allowed_everywhere={""},
        allowed=ImportInfo(internal={}, external={"archlint.utils": {"typing"}}),
        disallowed=ImportInfo(internal={"archlint.collection": {"archlint.utils"}}, external={}),
        grimp_cache="",
    )
cfg1 = Configuration(
    root_dir=Path("/home/frodo/projects/ring"),
    module_name="hello_world",
    module_root_dir=Path("/home/frodo/projects/ring/src/hello_world"),
    docs=DocsConfig(
        allow_additional=re.compile(r""),
        file_per_directory=re.compile(r"collapse_me"),
        file_per_class=re.compile(r"expand_me"),
        ignore=re.compile(r""),
        replace_double_underscore=True,
        md_dir=Path("docs/markdown"),
    ),
    imports=icfg1,
    methods=MethodsConfig(
        normal=9.0,
        ordering=(
            (re.compile(r""), 0.0),
            (re.compile(r""), 1.0),
        ),
    ),
    tests=TstsConfig(
        unit_dir=Path("tests/unit_tests"),
        allow_additional=re.compile(r""),
        ignore=re.compile(r""),
        file_per_class=re.compile(r"expand_me"),
        file_per_directory=re.compile(r"collapse_me"),
        function_per_class=re.compile(r""),
        replace_double_underscore=True,
        use_filename_suffix=False,
    ),
)
cfg2 = Configuration(
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
    tests=TstsConfig(
        unit_dir=Path(""),
        allow_additional=re.compile(r""),
        ignore=re.compile(r""),
        file_per_class=re.compile(r""),
        file_per_directory=re.compile(r""),
        function_per_class=re.compile(r""),
        replace_double_underscore=False,
        use_filename_suffix=False,
    ),
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
            Path("/some/expand_me/to/file.py"),
            "1",
            "CoolClass",
            "cool_method",
            re.compile(r"expand_me"),
            re.compile(r"collapse_me"),
            "/some/expand_me/to/file/coolclass_test.py:001:TestCoolClass.test_cool_method",
        ),
        (
            Path("/some/path/collapse_me/file.py"),
            "1",
            "CoolClass",
            "cool_method",
            re.compile(r"expand_me"),
            re.compile(r"collapse_me"),
            "/some/path/collapse_me_test.py:001:TestCoolClass.test_cool_method",
        ),
        (
            Path("/some/path/to/file.py"),
            "1",
            "CoolClass",
            "cool_method",
            re.compile(r"expand_me"),
            re.compile(r"collapse_me"),
            "/some/path/to/file_test.py:001:TestCoolClass.test_cool_method",
        ),
    ],
    ids=["file-per-class", "file-per-directory", "one-to-one"],
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
            Path("some/expand_me/to/file.py"),
            "1",
            "CoolClass",
            re.compile(r"expand_me"),
            re.compile(r"collapse_me"),
            "some/expand_me/to/file/coolclass.md:001:CoolClass",
        ),
        (
            Path("some/path/collapse_me/to/file.py"),
            "2",
            "CoolClass",
            re.compile(r"expand_me"),
            re.compile(r"collapse_me"),
            "some/path/collapse_me.md:002:CoolClass",
        ),
        (
            Path("/some/path/to/file.py"),
            "42",
            "CoolClass",
            re.compile(r"expand_me"),
            re.compile(r"collapse_me"),
            "/some/path/to/file.md:042:CoolClass",
        ),
    ],
    ids=["file-per-class", "file-per-directory", "one-to-one"],
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
        (
            Path("some/collapse_me/to/file.py"),
            "99",
            "cool_function",
            re.compile(r"collapse_me"),
            "some/collapse_me_test.py:099:test_cool_function",
        ),
        (
            Path("some/collapse_me/to/file.py"),
            "99",
            "cool_function",
            re.compile(r"no_match"),
            "some/collapse_me/to/file_test.py:099:test_cool_function",
        ),
    ],
    ids=["file-per-directory", "one-to-one"],
)
def test_make_test_function_path(
    path: Path,
    idx: str,
    func_name: str,
    file_per_directory: re.Pattern,
    expected: str,
):
    assert make_test_function_path(path, idx, func_name, file_per_directory) == expected


@pytest.mark.parametrize(
    "path, idx, func_name, file_per_directory, expected",
    [
        (
            Path("some/collapse_me/to/file.py"),
            "99",
            "cool_function",
            re.compile(r"collapse_me"),
            "some/collapse_me.md:099:cool_function",
        ),
        (
            Path("some/collapse_me/to/file.py"),
            "99",
            "cool_function",
            re.compile(r"no_match"),
            "some/collapse_me/to/file.md:099:cool_function",
        ),
    ],
    ids=["file-per-directory", "one-to-one"],
)
def test_make_doc_function_path(
    path: Path, idx: str, func_name: str, file_per_directory: re.Pattern, expected: str
):
    assert make_doc_function_path(path, idx, func_name, file_per_directory) == expected


@pytest.mark.parametrize(
    "config, pre, post",
    [
        (cfg1, "src/hello_world/submodule/file.py:001:greet", "tests/unit_tests/submodule/file_test.py:001:test_greet"),
        (cfg1, "src/hello_world/_file.py:001:Greeting", ""),
        (cfg1, "src/hello_world/path/file_.py:001:UpperNoDot", ""),
        (cfg1, "src/hello_world/__hello.py:999:__mangled", "tests/unit_tests/_hello_test.py:999:test_mangled"),
    ],
)
def test_map_to_test(config: Configuration, pre: str, post: str):
    assert map_to_test(pre, config) == post


@pytest.mark.parametrize(
    "config, pre, post",
    [
        (cfg1, "src/hello_world/path/file.py:001:greet", "docs/markdown/path/file.md:001:greet"),
        (cfg1, "path/file.py:001:Greet.greeter", "docs/markdown/path/file.md:001:Greet"),
        (cfg1, "path/file_.py:001:_private", "docs/markdown/path/file_.md:001:_private"),
        (cfg1, "_.py:999:__mangled", "docs/markdown/_.md:999:_mangled"),
    ],
)
def test_map_to_doc(config: Configuration, pre: str, post: str):
    assert map_to_doc(pre, config) == post


@pytest.mark.parametrize(
    "allowed, disallowed, allowed_everywhere, graph, expected",
    [
        ({"mod1": {"import1"}}, {}, {"allow_me"}, int_graph, {}),
        ({}, {"mod1": {"import1"}, "grimp": {"sys"}}, {"allow_me"}, ext_graph, {}),
        ({}, {}, {""}, "TODO", {}),
    ],
    ids=["a", "b", "c"],
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
    "config, module_name, disallowed_internal, disallowed_external",
    [
        (icfg1, "archlint", {"archlint.collection": {"archlint.utils"}}, {}),
        # (icfg1, "archlint", {}, {}),
        # (icfg1, "archlint", {}, {}),
        # (icfg1, "archlint", {}, {}),
    ],
    ids=["internal_violation"],
)
def test_get_disallowed_imports(config: ImportsConfig, module_name: str, disallowed_internal: dict[str, set[str]], disallowed_external: dict[str, set[str]]):
    violations_internal, violations_external = get_disallowed_imports(config, module_name)
    assert violations_internal == disallowed_internal
    assert violations_external == disallowed_external


@pytest.mark.parametrize(
    "method_dict, post, methods_cfg",
    [
        (
            {"method_a": "def method_a()", "method_b": "def method_b()"},
            ["method_b", "method_a"],
            MethodsConfig(
                normal=6.66,
                ordering=(
                    (re.compile(r"_b"), 0.0),
                    (re.compile(r"_a"), 1.0),
                ),
            ),
        ),
        (
            {"method_a": "def method_a()", "method_b": "def method_b()", "normal": "def normal(): ..."},
            ["method_a", "method_b", "normal"],
            MethodsConfig(
                normal=6.66,
                ordering=(
                    (re.compile(r"method_"), 0.0),
                ),
            ),
        ),
    ],
)
def test_sort_methods(method_dict: dict[str, str], post: list[str], methods_cfg: MethodsConfig):
    assert sort_methods(method_dict, methods_cfg) == post


@pytest.mark.parametrize(
    "expected, actual, allow_additional, missing, unexpected, overlap",
    [
        (["a", "b", "c"], ["a", "b", "c"], re.compile(r"additional"), [], [], {"a", "b", "c"}),
        (["a", "b", "c"], ["a", "c"], re.compile(r"additional"), ["b"], [], {"a", "c"}),
        (["a", "c"], ["a", "b", "c"], re.compile(r"additional"), [], ["b"], {"a", "c"}),
        (["a", "c"], ["a", "b"], re.compile(r"additional"), ["c"], ["b"], {"a"}),
    ],
    ids=["0", "1", "2", "3"]
)
def test_analyze_discrepancies(
    expected: list[str],
    actual: list[str],
    allow_additional: re.Pattern,
    missing: list[str],
    unexpected: list[str],
    overlap: set[str],
):
    result = analyze_discrepancies(expected, actual, allow_additional)
    assert result == (missing, unexpected, overlap)
