"""
Configuration types and helper functions.

Goal is to perform strict validation and helpful error messages.
"""

import re
import tomllib
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import cast

from .regexes import Regex
from .utils import (
    assert_bool,
    compile_for_path_segment,
    compile_string_or_bool,
    get_project_root,
    make_regex,
    prepend_module_name,
)


@dataclass
class DocsConfig:
    allow_additional: re.Pattern
    """ Whether/which additional documentation files and objects should be allowed. """

    file_per_directory: re.Pattern
    """ Regular expression matching any directories that should be collapsed to a single .md file. """

    file_per_class: re.Pattern
    """ Regular expression matching any classes (including path) that should be
        promoted to thir own .md file."""

    ignore: re.Pattern
    """
    Regular expression matching any files or objects that should not be included in the
        analysis of documentation structure.
    """
    replace_double_underscore: bool
    """ Whether """
    md_dir: Path


@dataclass
class ImportInfo:
    internal: dict[str, set[str]]
    external: dict[str, set[str]]


@dataclass
class ImportsConfig:
    internal_allowed_everywhere: set[str]
    external_allowed_everywhere: set[str]
    allowed: ImportInfo
    disallowed: ImportInfo
    grimp_cache: str


@dataclass
class MethodsConfig:
    normal: float
    ordering: tuple[tuple[re.Pattern, float], ...]


@dataclass
class TestsConfig:
    allow_additional: re.Pattern
    ignore: re.Pattern
    file_per_class: re.Pattern
    file_per_directory: re.Pattern
    function_per_class: re.Pattern
    replace_double_underscore: bool
    unit_dir: Path
    use_filename_suffix: bool


@dataclass
class Configuration:
    root_dir: Path
    module_name: str
    docs: DocsConfig
    tests: TestsConfig
    imports: ImportsConfig
    methods: MethodsConfig
    module_root_dir: Path


def get_docs_config(raw_pyproject_docs: dict) -> DocsConfig:
    DEFAULTS = {
        "md_dir": "docs/md",
        "allow_additional": False,
        "ignore": "",
        "file_per_directory": "",
        "file_per_class": "",
        "replace_double_underscore": False,
    }
    raw = DEFAULTS | raw_pyproject_docs
    return DocsConfig(
        md_dir=Path(raw["md_dir"]).absolute(),
        allow_additional=compile_string_or_bool(raw["allow_additional"]),
        ignore=compile_for_path_segment(raw["ignore"]),
        file_per_directory=compile_for_path_segment(raw["file_per_directory"]),
        file_per_class=compile_for_path_segment(raw["file_per_class"]),
        replace_double_underscore=assert_bool(raw["replace_double_underscore"]),
    )


def get_imports_config(raw_imports_config: dict, module_name: str) -> ImportsConfig:
    def fix_internal(d: dict[str, list[str]], mod_name: str) -> dict[str, set[str]]:
        prepend_name = partial(prepend_module_name, module_name=mod_name)
        return {prepend_name(k): set(map(prepend_name, v)) for k, v in d.items()}

    def fix_external(d: dict[str, list[str]], mod_name: str) -> dict[str, set[str]]:
        return {prepend_module_name(k, mod_name): set(v) for k, v in d.items()}

    return ImportsConfig(
        internal_allowed_everywhere=set(
            map(
                partial(prepend_module_name, module_name=module_name),
                raw_imports_config.get("internal_allowed_everywhere", ""),
            )
        ),
        external_allowed_everywhere=set(
            cast(list[str], raw_imports_config.get("external_allowed_everywhere", ""))
        ),
        allowed=ImportInfo(
            internal=fix_internal(
                raw_imports_config["allowed"].get("internal", {}), mod_name=module_name
            ),
            external=fix_external(
                raw_imports_config["allowed"].get("external", {}), mod_name=module_name
            ),
        ),
        disallowed=ImportInfo(
            internal=fix_internal(
                raw_imports_config["disallowed"].get("internal", {}), mod_name=module_name
            ),
            external=fix_external(
                raw_imports_config["disallowed"].get("external", {}), mod_name=module_name
            ),
        ),
        grimp_cache=raw_imports_config.get("grimp_cache", ".grimp_cache"),
    )


def get_methods_config(pyproject_methods_config: dict) -> MethodsConfig:
    DEFAULT_VALUE = 99.0

    custom_mapping = pyproject_methods_config.get("custom_order", {})
    custom = [(make_regex(k), float(v)) for k, v in custom_mapping.items()]
    builtins_mapping = pyproject_methods_config.get("builtins_order", {})
    predefined = [
        (regexpr, float(builtins_mapping.get(value, DEFAULT_VALUE)))
        for regexpr, value in (
            (Regex.methods.INIT, "init"),
            (Regex.methods.ABSTRACT_DUNDER, "abstract_dunder"),
            (Regex.methods.ABSTRACT_PROPERTY, "abstract_property"),
            (Regex.methods.ABSTRACT_PRIVATE_PROPERTY, "abstract_private_property"),
            (Regex.methods.ABSTRACT_CLASSMETHOD, "abstract_classmethod"),
            (Regex.methods.ABSTRACT_STATIC, "abstract_static"),
            (Regex.methods.ABSTRACT_PRIVATE, "abstract_private"),
            (Regex.methods.DUNDER, "dunder"),
            (Regex.methods.PRIVATE, "private"),
            (Regex.methods.MANGLED, "mangled"),
            (Regex.methods.CLASSMETHOD, "classmethod"),
            (Regex.methods.PRIVATE_PROPERTY, "private_property"),
            (Regex.methods.PROPERTY, "property"),
            (Regex.methods.STATIC, "static"),
            (Regex.methods.FINAL, "final"),
            (Regex.methods.ABSTRACT, "abstract"),
        )
    ]

    return MethodsConfig(
        normal=float(builtins_mapping.get("normal", DEFAULT_VALUE)),
        ordering=tuple(custom + predefined),
    )


def get_tests_config(pyproject_archlint_tests: dict) -> TestsConfig:
    DEFAULTS = {
        "unit_dir": "tests/unit",
        "allow_additional": False,
        "ignore": "",
        "file_per_class": "",
        "file_per_directory": "",
        "function_per_class": "",
        "replace_double_underscore": False,
        "use_filename_suffix": True,
    }
    raw = DEFAULTS | pyproject_archlint_tests
    return TestsConfig(
        unit_dir=Path(raw["unit_dir"]).absolute(),
        allow_additional=compile_string_or_bool(raw["allow_additional"]),
        ignore=compile_for_path_segment(raw["ignore"]),
        file_per_class=compile_for_path_segment(raw["file_per_class"]),
        file_per_directory=compile_for_path_segment(raw["file_per_directory"]),
        function_per_class=compile_for_path_segment(raw["function_per_class"]),
        replace_double_underscore=assert_bool(raw["replace_double_underscore"]),
        use_filename_suffix=assert_bool(raw["use_filename_suffix"]),
    )


def get_config(project_root: Path | None = None) -> Configuration:
    root_dir: Path = project_root or get_project_root()
    raw_pyproject: dict = tomllib.loads((root_dir / "pyproject.toml").read_text())
    default_module_name = raw_pyproject["project"]["name"].replace("-", "_")
    raw_config = raw_pyproject["tool"]["archlint"]

    return Configuration(
        root_dir=root_dir,
        module_root_dir=root_dir / "src" / default_module_name,
        module_name=raw_config.get("module_name", default_module_name),
        docs=get_docs_config(raw_config.get("docs", {})),
        imports=get_imports_config(raw_config.get("imports", {}), default_module_name),
        tests=get_tests_config(raw_config.get("tests", {})),
        methods=get_methods_config(raw_config.get("methods", {})),
    )
