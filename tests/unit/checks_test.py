import re
from pathlib import Path
from unittest.mock import patch

import grimp
import pytest

from archlint.checks import (
    check_docs_structure,
    check_imports,
    check_method_order,
    check_tests_structure,
)
from archlint.collection import Objects
from archlint.configuration import (
    Configuration,
    DocsConfig,
    ImportInfo,
    ImportsConfig,
    MethodsConfig,
    TstsConfig,
)

icfg_base = ImportsConfig(
    internal_allowed_everywhere={""},
    external_allowed_everywhere={""},
    allowed=ImportInfo(internal={}, external={}),
    disallowed=ImportInfo(internal={}, external={}),
    grimp_cache="",
)
cfg_base = Configuration(
    root_dir=Path(""),
    module_name="",
    module_root_dir=Path(""),
    docs=DocsConfig(
        md_dir=Path("documentation/markdown"),
        allow_additional=re.compile(r"allow_me"),
        file_per_directory=re.compile(r"collapse_me"),
        file_per_class=re.compile(r"expand_me"),
        ignore=re.compile(r"ignore_me"),
        replace_double_underscore=False,
    ),
    imports=icfg_base,
    methods=MethodsConfig(
        normal=9.0,
        ordering=(
            (re.compile(r"put_me_first"), 0.0),
            (re.compile(r"__init__"), 1.0),
            (re.compile(r"put_me_last"), 2.0),
        ),
    ),
    tests=TstsConfig(
        unit_dir=Path(""),
        allow_additional=re.compile(r""),
        ignore=re.compile(r""),
        file_per_class=re.compile(r"expand_me"),
        file_per_directory=re.compile(r"collapse_me"),
        function_per_class=re.compile(r""),
        replace_double_underscore=False,
        use_filename_suffix=False,
    ),
)
cfg_alt = Configuration(
    root_dir=Path(""),
    module_name="",
    module_root_dir=Path(""),
    docs=DocsConfig(
        md_dir=Path("documentation/markdown"),
        allow_additional=re.compile(r"allow_me"),
        file_per_directory=re.compile(r"collapse_me"),
        file_per_class=re.compile(r"expand_me"),
        ignore=re.compile(r"ignore_me"),
        replace_double_underscore=False,
    ),
    imports=icfg_base,
    methods=MethodsConfig(
        normal=9.0,
        ordering=(
            (re.compile(r"put_me_first"), 0.0),
            (re.compile(r"middle"), 1.0),
            (re.compile(r"put_me_last"), 2.0),
        ),
    ),
    tests=TstsConfig(
        unit_dir=Path(""),
        allow_additional=re.compile(r""),
        ignore=re.compile(r""),
        file_per_class=re.compile(r"expand_me"),
        file_per_directory=re.compile(r"collapse_me"),
        function_per_class=re.compile(r""),
        replace_double_underscore=False,
        use_filename_suffix=False,
    ),
)
functions_baseline = [
    (Path("src/module/submodule"), 1, "func1"),
    (Path("src/module/submodule"), 1, "func_2"),
    (Path("src/module/submodule"), 1, "function3"),
]
functions_baseline_docs = [
    (Path("docs/markdown/submodule"), 1, "func1"),
    (Path("docs/markdown/submodule"), 1, "func_2"),
    (Path("docs/markdown/submodule"), 1, "function3"),
]
functions_baseline_tests = [
    (Path("tests/unit_tests/submodule"), 1, "func1"),
    (Path("tests/unit_tests/submodule"), 1, "func_2"),
    (Path("tests/unit_tests/submodule"), 1, "function3"),
]
functions_missing_docs = [
    (Path("docs/markdown/submodule"), 1, "func1"),
    (Path("docs/markdown/submodule"), 1, "function3"),
]
functions_missing_tests = [
    (Path("tests/unit_tests/submodule"), 1, "func1"),
    (Path("tests/unit_tests/submodule"), 1, "function3"),
]
functions_unexpected_docs = [
    (Path("src/module/submodule"), 1, "func1"),
    (Path("src/module/submodule"), 1, "func_unmatched"),
    (Path("src/module/submodule"), 1, "func_2"),
    (Path("src/module/submodule"), 1, "function3"),
]
functions_unexpected_tests = [
    (Path("tests/unit_tests/submodule"), 1, "func1"),
    (Path("tests/unit_tests/submodule"), 1, "func_unmatched"),
    (Path("tests/unit_tests/submodule"), 1, "function3"),
]
functions_mixed_tests = [
    (Path("tests/unit_tests/submodule"), 1, "func1"),
    (Path("tests/unit_tests/submodule"), 1, "func_unmatched"),
    (Path("tests/unit_tests/submodule"), 1, "func_2"),
    (Path("tests/unit_tests/submodule"), 1, "function3"),
]
functions_mixed_docs = [
    (Path("src/module/submodule"), 1, "func1"),
    (Path("src/module/submodule"), 1, "func_unmatched"),
    (Path("src/module/submodule"), 1, "function3"),
]
classes_baseline = [
    (
        Path("src/module/submodule"),
        1,
        "func_unmatched",
        ["method_a", "method_b", "method_c"],
        {
            "method_a": "@property\n    def method_a(self):\n        ",
            "method_b": "@abstractmethod\n    def method_b(self): ...\n        ",
            "method_c": "def method_c(self):\n        print()",
        },
        ["inherited_a", "inherited_b"],
    ),
    (
        Path("src/module/submodule"),
        1,
        "ClassA",
        ["method_a", "method_b", "method_c"],
        {
            "method_a": "@property\n    def method_a(self):\n        ",
            "method_b": "@abstractmethod\n    def method_b(self): ...\n        ",
            "method_c": "def method_c(self):\n        print()",
        },
        ["inherited_a", "inherited_b"],
    ),
    (
        Path("src/module/submodule"),
        1,
        "ClassB",
        ["method_a", "method_b", "method_c"],
        {
            "method_a": "@property\n    def method_a(self):\n        ",
            "method_b": "@abstractmethod\n    def method_b(self): ...\n        ",
            "method_c": "def method_c(self):\n        print()",
        },
        ["inherited_a", "inherited_b"],
    ),
]
classes_baseline_docs = [
    (
        Path("docs/markdown/submodule"),
        1,
        "func_unmatched",
        ["method_a", "method_b", "method_c"],
        {
            "method_a": "@property\n    def method_a(self):\n        ",
            "method_b": "@abstractmethod\n    def method_b(self): ...\n        ",
            "method_c": "def method_c(self):\n        print()",
        },
        ["inherited_a", "inherited_b"],
    ),
    (
        Path("docs/markdown/submodule"),
        1,
        "ClassA",
        ["method_a", "method_b", "method_c"],
        {
            "method_a": "@property\n    def method_a(self):\n        ",
            "method_b": "@abstractmethod\n    def method_b(self): ...\n        ",
            "method_c": "def method_c(self):\n        print()",
        },
        ["inherited_a", "inherited_b"],
    ),
    (
        Path("docs/markdown/submodule"),
        1,
        "ClassB",
        ["method_a", "method_b", "method_c"],
        {
            "method_a": "@property\n    def method_a(self):\n        ",
            "method_b": "@abstractmethod\n    def method_b(self): ...\n        ",
            "method_c": "def method_c(self):\n        print()",
        },
        ["inherited_a", "inherited_b"],
    ),
]
classes_baseline_tests = [
    (
        Path("tests/unit_tests/submodule"),
        1,
        "func_unmatched",
        ["method_a", "method_b", "method_c"],
        {
            "method_a": "@property\n    def method_a(self):\n        ",
            "method_b": "@abstractmethod\n    def method_b(self): ...\n        ",
            "method_c": "def method_c(self):\n        print()",
        },
        ["inherited_a", "inherited_b"],
    ),
    (
        Path("tests/unit_tests/submodule"),
        1,
        "ClassA",
        ["method_a", "method_b", "method_c"],
        {
            "method_a": "@property\n    def method_a(self):\n        ",
            "method_b": "@abstractmethod\n    def method_b(self): ...\n        ",
            "method_c": "def method_c(self):\n        print()",
        },
        ["inherited_a", "inherited_b"],
    ),
    (
        Path("tests/unit_tests/submodule"),
        1,
        "ClassB",
        ["method_a", "method_b", "method_c"],
        {
            "method_a": "@property\n    def method_a(self):\n        ",
            "method_b": "@abstractmethod\n    def method_b(self): ...\n        ",
            "method_c": "def method_c(self):\n        print()",
        },
        ["inherited_a", "inherited_b"],
    ),
]
classes_missing_docs = [
    (
        Path("docs/markdown/submodule"),
        1,
        "func_unmatched",
        ["method_a", "method_b", "method_c"],
        {
            "method_a": "@property\n    def method_a(self):\n        ",
            "method_b": "@abstractmethod\n    def method_b(self): ...\n        ",
            "method_c": "def method_c(self):\n        print()",
        },
        ["inherited_a", "inherited_b"],
    ),
    (
        Path("docs/markdown/submodule"),
        1,
        "ClassA",
        ["method_a", "method_b", "method_c"],
        {
            "method_a": "@property\n    def method_a(self):\n        ",
            "method_b": "@abstractmethod\n    def method_b(self): ...\n        ",
            "method_c": "def method_c(self):\n        print()",
        },
        ["inherited_a", "inherited_b"],
    ),
    (
        Path("docs/markdown/submodule"),
        1,
        "ClassB",
        ["method_a", "method_b", "method_c"],
        {
            "method_a": "@property\n    def method_a(self):\n        ",
            "method_c": "def method_c(self):\n        print()",
        },
        ["inherited_a", "inherited_b"],
    ),
]
classes_missing_tests = [
    (
        Path("tests/unit_tests/submodule"),
        1,
        "func_unmatched",
        ["method_a", "method_b", "method_c"],
        {
            "method_a": "@property\n    def method_a(self):\n        ",
            "method_b": "@abstractmethod\n    def method_b(self): ...\n        ",
            "method_c": "def method_c(self):\n        print()",
        },
        ["inherited_a", "inherited_b"],
    ),
    (
        Path("tests/unit_tests/submodule"),
        1,
        "ClassA",
        ["method_a", "method_b", "method_c"],
        {
            "method_a": "@property\n    def method_a(self):\n        ",
            "method_b": "@abstractmethod\n    def method_b(self): ...\n        ",
            "method_c": "def method_c(self):\n        print()",
        },
        ["inherited_a", "inherited_b"],
    ),
    (
        Path("tests/unit_tests/submodule"),
        1,
        "ClassB",
        ["method_a", "method_b", "method_c"],
        {
            "method_a": "@property\n    def method_a(self):\n        ",
            "method_c": "def method_c(self):\n        print()",
        },
        ["inherited_a", "inherited_b"],
    ),
]
classes_unexpected_docs = [
    (
        Path("docs/markdown/submodule"),
        1,
        "func_unmatched",
        ["method_a", "method_b", "method_c"],
        {
            "method_a": "@property\n    def method_a(self):\n        ",
            "method_b": "@abstractmethod\n    def method_b(self): ...\n        ",
            "method_c": "def method_c(self):\n        print()",
        },
        ["inherited_a", "inherited_b"],
    ),
    (
        Path("docs/markdown/submodule"),
        1,
        "ClassA",
        ["method_a", "method_b", "method_c"],
        {
            "method_a": "@property\n    def method_a(self):\n        ",
            "method_b": "@abstractmethod\n    def method_b(self): ...\n        ",
            "method_c": "def method_c(self):\n        print()",
        },
        ["inherited_a", "inherited_b"],
    ),
    (
        Path("docs/markdown/submodule"),
        1,
        "ClassB",
        ["method_a", "method_b", "method_c"],
        {
            "method_a": "@property\n    def method_a(self):\n        ",
            "method_b": "@abstractmethod\n    def method_b(self): ...\n        ",
            "method_c": "def method_c(self):\n        print()",
            "method_d": "def method_d(self):\n        print()",
        },
        ["inherited_a", "inherited_b"],
    ),
]
classes_unexpected_tests = [
    (
        Path("tests/unit_tests/submodule"),
        1,
        "func_unmatched",
        ["method_a", "method_b", "method_c"],
        {
            "method_a": "@property\n    def method_a(self):\n        ",
            "method_b": "@abstractmethod\n    def method_b(self): ...\n        ",
            "method_c": "def method_c(self):\n        print()",
        },
        ["inherited_a", "inherited_b"],
    ),
    (
        Path("tests/unit_tests/submodule"),
        1,
        "ClassA",
        ["method_a", "method_b", "method_c"],
        {
            "method_a": "@property\n    def method_a(self):\n        ",
            "method_b": "@abstractmethod\n    def method_b(self): ...\n        ",
            "method_c": "def method_c(self):\n        print()",
        },
        ["inherited_a", "inherited_b"],
    ),
    (
        Path("tests/unit_tests/submodule"),
        1,
        "ClassB",
        ["method_a", "method_b", "method_c"],
        {
            "method_a": "@property\n    def method_a(self):\n        ",
            "method_b": "@abstractmethod\n    def method_b(self): ...\n        ",
            "method_c": "def method_c(self):\n        print()",
            "method_d": "def method_d(self):\n        print()",
        },
        ["inherited_a", "inherited_b"],
    ),
]
classes_mixed_docs = [
    (
        Path("docs/markdown/submodule"),
        1,
        "func_unmatched",
        ["method_a", "method_b", "method_c"],
        {
            "method_a": "@property\n    def method_a(self):\n        ",
            "method_b": "@abstractmethod\n    def method_b(self): ...\n        ",
            "method_c": "def method_c(self):\n        print()",
        },
        ["inherited_a", "inherited_b"],
    ),
    (
        Path("docs/markdown/submodule"),
        1,
        "ClassA",
        ["method_a", "method_b", "method_c"],
        {
            "method_a": "@property\n    def method_a(self):\n        ",
            "method_b": "@abstractmethod\n    def method_b(self): ...\n        ",
            "method_c": "def method_c(self):\n        print()",
        },
        ["inherited_a", "inherited_b"],
    ),
    (
        Path("docs/markdown/submodule"),
        1,
        "ClassB",
        ["method_a", "method_b", "method_c"],
        {
            "method_a": "@property\n    def method_a(self):\n        ",
            "method_b": "@abstractmethod\n    def method_b(self): ...\n        ",
            "method_c": "def method_c(self):\n        print()",
        },
        ["inherited_a", "inherited_b"],
    ),
]
classes_mixed_tests = [
    (
        Path("tests/unit_tests/submodule"),
        1,
        "func_unmatched",
        ["method_a", "method_b", "method_c"],
        {
            "method_a": "@property\n    def method_a(self):\n        ",
            "method_b": "@abstractmethod\n    def method_b(self): ...\n        ",
            "method_c": "def method_c(self):\n        print()",
        },
        ["inherited_a", "inherited_b"],
    ),
    (
        Path("tests/unit_tests/submodule"),
        1,
        "ClassA",
        ["method_a", "method_b", "method_c"],
        {
            "method_a": "@property\n    def method_a(self):\n        ",
            "method_b": "@abstractmethod\n    def method_b(self): ...\n        ",
            "method_c": "def method_c(self):\n        print()",
        },
        ["inherited_a", "inherited_b"],
    ),
    (
        Path("tests/unit_tests/submodule"),
        1,
        "ClassB",
        ["method_a", "method_b", "method_c"],
        {
            "method_a": "@property\n    def method_a(self):\n        ",
            "method_b": "@abstractmethod\n    def method_b(self): ...\n        ",
            "method_c": "def method_c(self):\n        print()",
        },
        ["inherited_a", "inherited_b"],
    ),
]
classes_out_of_order = [
    (
        Path("src/model.py"),
        0,
        "User",
        ["private_method", "__init__", "put_me_first"],
        {
            "private_method": "def _private_method(self):",
            "__init__": "def __init__(self):",
            "put_me_first": "def put_me_first(self):",
        },
        [],
    )
]
match_output = [re.compile(r"No problems detected", re.DOTALL)]
missing_output = [
    re.compile(r"MISSING.+?funct_2", re.DOTALL),
    re.compile(r"MISSING.+?ClassB\.method_b", re.DOTALL),
]
unexpected_output = [
    re.compile(r"UNEXPECTED.+?func_unexpected", re.DOTALL),
    re.compile(r"UNEXPECTED.+?ClassB\.method_d", re.DOTALL),
]
mixed_output = [
    re.compile(r"MISSING.+?funct_2", re.DOTALL),
    re.compile(r"MISSING.+?ClassB\.method_b", re.DOTALL),
    re.compile(r"UNEXPECTED.+?func_unexpected", re.DOTALL),
    re.compile(r"UNEXPECTED.+?ClassB\.method_d", re.DOTALL),
]


@pytest.mark.parametrize(
    "cfg, source_objects, contained, not_contained, problems",
    [
        (
            cfg_base,
            Objects(
                functions=[],
                classes=classes_baseline,
            ),
            [],
            ["public_method"],
            False,
        ),
        (
            cfg_base,
            Objects(
                functions=[],
                classes=classes_out_of_order,
            ),
            ["__init__", "put_me_first"],
            [],
            True,
        ),
        # (
        #     cfg_base,
        #     Objects(functions=[], classes=[]),
        #     [],
        #     [],
        # ),
        # (
        #     cfg_base,
        #     Objects(functions=[], classes=[]),
        #     [],
        #     [],
        # ),
    ],
    ids=["in_order", "out_of_order"],  # , "multiple_classes_mixed", "no_classes"],
)
def test_check_method_order(
    cfg: Configuration,
    source_objects: Objects,
    contained: list[str | re.Pattern],
    not_contained: list[str | re.Pattern],
    problems: bool,
):
    result, result_problems = check_method_order(cfg, source_objects)
    for search_string in contained:
        assert re.search(search_string, result)
    for search_string in not_contained:
        assert not re.search(search_string, result)
    assert result_problems is problems


@pytest.mark.parametrize(
    "cfg, source_objects, docs_objects, contained, not_contained, problems",
    [
        (
            cfg_base,
            Objects(functions=functions_baseline, classes=classes_baseline),
            Objects(functions=functions_baseline_tests, classes=classes_baseline_tests),
            match_output,
            mixed_output,
            False,
        ),
        (
            cfg_base,
            Objects(functions=functions_baseline, classes=classes_baseline),
            Objects(functions=functions_missing_tests, classes=classes_missing_tests),
            missing_output,
            unexpected_output + match_output,
            True,
        ),
        (
            cfg_base,
            Objects(functions=functions_baseline, classes=classes_baseline),
            Objects(functions=functions_unexpected_tests, classes=classes_unexpected_tests),
            unexpected_output,
            missing_output + match_output,
            True,
        ),
        (
            cfg_base,
            Objects(functions=functions_baseline, classes=classes_baseline),
            Objects(functions=functions_mixed_tests, classes=classes_mixed_tests),
            mixed_output,
            match_output,
            True,
        ),
        (
            cfg_alt,
            Objects(functions=functions_baseline, classes=classes_baseline),
            Objects(functions=functions_mixed_tests, classes=classes_mixed_tests),
            match_output,
            mixed_output,
            False,
        ),
    ],
    ids=[
        "perfect_match",
        "missing_only",
        "unexpected_only",
        "missing_and_unexpected",
        "with_ignore",
    ],
)
def test_check_docs_structure(
    cfg: Configuration,
    source_objects: Objects,
    docs_objects: Objects,
    contained: list[str | re.Pattern],
    not_contained: list[str | re.Pattern],
    problems: bool,
):
    result, result_problems = check_docs_structure(cfg, source_objects, docs_objects)
    for search_string in contained:
        assert re.search(search_string, result)
    for search_string in not_contained:
        assert not re.search(search_string, result)
    assert result_problems is problems


@pytest.mark.parametrize(
    "cfg, source_objects, docs_objects, contained, not_contained, problems",
    [
        (
            cfg_base,
            Objects(functions=functions_baseline, classes=classes_baseline),
            Objects(functions=functions_baseline_docs, classes=classes_baseline_docs),
            match_output,
            mixed_output,
            False,
        ),
        (
            cfg_base,
            Objects(functions=functions_baseline, classes=classes_baseline),
            Objects(functions=functions_missing_docs, classes=classes_missing_docs),
            missing_output,
            unexpected_output + match_output,
            True,
        ),
        (
            cfg_base,
            Objects(functions=functions_baseline, classes=classes_baseline),
            Objects(functions=functions_unexpected_docs, classes=classes_unexpected_docs),
            unexpected_output,
            missing_output + match_output,
            True,
        ),
        (
            cfg_base,
            Objects(functions=functions_baseline, classes=classes_baseline),
            Objects(functions=functions_mixed_docs, classes=classes_mixed_docs),
            mixed_output,
            match_output,
            True,
        ),
        (
            cfg_alt,
            Objects(functions=functions_baseline, classes=classes_baseline),
            Objects(functions=functions_mixed_docs, classes=classes_mixed_docs),
            match_output,
            mixed_output,
            False,
        ),
    ],
    ids=[
        "perfect_match",
        "missing_only",
        "unexpected_only",
        "missing_and_unexpected",
        "with_ignore",
    ],
)
def test_check_tests_structure(
    cfg: Configuration,
    source_objects: Objects,
    docs_objects: Objects,
    contained: list[str | re.Pattern],
    not_contained: list[str | re.Pattern],
    problems: bool,
):
    result, result_problems = check_tests_structure(cfg, source_objects, docs_objects)
    for search_string in contained:
        assert re.search(search_string, result)
    for search_string in not_contained:
        assert not re.search(search_string, result)
    assert result_problems is problems


@pytest.mark.parametrize(
    "config, module_name, internal_violations, external_violations, contained, not_contained, problems",
    [
        (
            icfg_base,
            "hello",
            {},
            {},
            ["No problems detected"],
            [""],
            False,
        ),
        (
            icfg_base,
            "hello",
            {"cool_module": {"hello.forbidden"}},
            {},
            ["hello.forbidden"],
            [],
            True,
        ),
        (
            icfg_base,
            "hello_world",
            {},
            {"cool_module": {"forbidden_external"}},
            ["forbidden_external"],
            ["hello_world"],
            True,
        ),
        (
            icfg_base,
            "hello_world",
            {"cool_module": {"hello_world.forbidden"}},
            {"cool_module": {"forbidden_external"}},
            ["hello_world.forbidden", "forbidden_external"],
            [],
            True,
        ),
    ],
    ids=[
        "no_violations",
        "internal_violations",
        "external_violations",
        "internal_and_external",
    ],
)
def test_check_imports(
    config: ImportsConfig,
    module_name: str,
    internal_violations: dict[str, set[str]],
    external_violations: dict[str, set[str]],
    contained: list[str | re.Pattern],
    not_contained: list[str | re.Pattern],
    problems: bool,
):
    with patch("archlint.logic.get_disallowed_imports") as mock_collector:
        mock_collector.return_value = (internal_violations, external_violations)

        result, result_problems = check_imports(config, module_name)
        for search_string in contained:
            assert re.search(search_string, result)
        for search_string in not_contained:
            assert not re.search(search_string, result)
        assert result_problems is problems
