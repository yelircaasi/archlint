import re
import tomllib
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from re import Pattern
from typing import cast

from .regexes import Regex
from .utils import (
    assert_bool,
    compile_for_path_segment,
    get_project_root,
    make_regex,
    prepend_module_name,
)


@dataclass
class ImportInfo:
    internal: dict[str, set[str]]
    external: dict[str, set[str]]


@dataclass
class ImportConfig:
    internal_allowed_everywhere: set[str]
    external_allowed_everywhere: set[str]
    allowed: ImportInfo
    disallowed: ImportInfo
    grimp_cache: str


def get_import_config(raw_config: dict, module_name: str) -> ImportConfig:
    def fix_internal(d: dict[str, list[str]], mod_name: str) -> dict[str, set[str]]:
        prepend_name = partial(prepend_module_name, module_name=mod_name)
        return {prepend_name(k): set(map(prepend_name, v)) for k, v in d.items()}

    def fix_external(d: dict[str, list[str]], mod_name: str) -> dict[str, set[str]]:
        return {prepend_module_name(k, mod_name): set(v) for k, v in d.items()}

    raw_import_config = raw_config["imports"]

    return ImportConfig(
        internal_allowed_everywhere=set(
            map(
                partial(prepend_module_name, module_name=module_name),
                raw_import_config["internal_allowed_everywhere"],
            )
        ),
        external_allowed_everywhere=set(
            cast(list[str], raw_import_config["external_allowed_everywhere"])
        ),
        allowed=ImportInfo(
            internal=fix_internal(
                raw_import_config["allowed"].get("internal", {}), mod_name=module_name
            ),
            external=fix_external(
                raw_import_config["allowed"].get("external", {}), mod_name=module_name
            ),
        ),
        disallowed=ImportInfo(
            internal=fix_internal(
                raw_import_config["disallowed"].get("internal", {}), mod_name=module_name
            ),
            external=fix_external(
                raw_import_config["disallowed"].get("external", {}), mod_name=module_name
            ),
        ),
        grimp_cache=raw_import_config.get("grimp_cache", ".grimp_cache"),
    )


# METHOD ORDER


@dataclass
class MethodOrderConfig:
    normal: float
    ordering: tuple[tuple[re.Pattern, float], ...]


def get_method_order_config(raw_config: dict) -> MethodOrderConfig:
    raw_mo_config = raw_config["method_order"]
    DEFAULT_VALUE = 99.9

    custom = [(make_regex(k), float(v)) for k, v in raw_mo_config["regex"].items()]
    predefined = [
        (regexpr, float(raw_mo_config.get(value, DEFAULT_VALUE)))
        for regexpr, value in (
            (Regex.INIT, "init"),
            (Regex.ABSTRACT_DUNDER, "abstract_dunder"),
            (Regex.ABSTRACT_PROPERTY, "abstract_property"),
            (Regex.ABSTRACT_PRIVATE_PROPERTY, "abstract_private_property"),
            (Regex.ABSTRACT_CLASSMETHOD, "abstract_classmethod"),
            (Regex.ABSTRACT_STATIC, "abstract_static"),
            (Regex.ABSTRACT_PRIVATE, "abstract_private"),
            (Regex.DUNDER, "dunder"),
            (Regex.PRIVATE, "private"),
            (Regex.MANGLED, "mangled"),
            (Regex.CLASSMETHOD, "classmethod"),
            (Regex.PRIVATE_PROPERTY, "private_property"),
            (Regex.PROPERTY, "property"),
            (Regex.STATIC, "static"),
            (Regex.FINAL, "final"),
            (Regex.ABSTRACT, "abstract"),
        )
    ]

    return MethodOrderConfig(
        normal=float(raw_mo_config["normal"]),
        ordering=tuple(custom + predefined),
    )


# STRUCTURE


@dataclass
class TestsConfig:
    allow_additional: bool
    file_per_class: Pattern
    file_per_directory: Pattern
    function_for_class: Pattern
    ignore: Pattern
    keep_double_underscore: bool
    unit_dir: Path
    use_filename_suffix: bool


@dataclass
class DocsConfig:
    allow_additional: bool
    file_per_directory: Pattern
    file_per_class: Pattern
    ignore: Pattern
    keep_double_underscore: bool
    md_dir: Path


def get_tests_config(raw_pyproject: dict, project_root: Path) -> TestsConfig:
    return TestsConfig(
        allow_additional=assert_bool(raw_pyproject["tests"]["allow_additional"]),
        # compile_for_path_segment_or_bool(raw_pyproject["tests"]["allow_additional"]),
        file_per_class=compile_for_path_segment(raw_pyproject["tests"]["file_per_class"]),
        file_per_directory=compile_for_path_segment(raw_pyproject["tests"]["file_per_directory"]),
        function_for_class=compile_for_path_segment(raw_pyproject["tests"]["function_for_class"]),
        ignore=compile_for_path_segment(raw_pyproject["tests"]["ignore"]),
        keep_double_underscore=assert_bool(raw_pyproject["tests"]["keep_double_underscore"]),
        unit_dir=Path(raw_pyproject["tests"]["unit_dir"]).absolute(),
        use_filename_suffix=assert_bool(raw_pyproject["tests"]["use_filename_suffix"]),
    )


def get_docs_config(raw_pyproject: dict, project_root: Path) -> DocsConfig:
    return DocsConfig(
        allow_additional=assert_bool(raw_pyproject["docs"]["allow_additional"]),
        # compile_for_path_segment_or_bool(raw_pyproject["docs"]["allow_additional"]),
        file_per_directory=compile_for_path_segment(raw_pyproject["docs"]["file_per_directory"]),
        file_per_class=compile_for_path_segment(raw_pyproject["docs"]["file_per_class"]),
        ignore=compile_for_path_segment(raw_pyproject["docs"]["ignore"]),
        keep_double_underscore=assert_bool(raw_pyproject["docs"]["keep_double_underscore"]),
        md_dir=Path(raw_pyproject["docs"]["md_dir"]).absolute(),
    )


@dataclass
class Configuration:
    root_dir: Path
    module_name: str
    docs: DocsConfig
    tests: TestsConfig
    imports: ImportConfig
    method_order: MethodOrderConfig
    module_root_dir: Path


def get_config(project_root: Path | None = None) -> Configuration:
    root_dir: Path = project_root or get_project_root()
    raw_pyproject: dict = tomllib.loads((root_dir / "pyproject.toml").read_text())
    module_name = raw_pyproject["project"]["name"].replace("-", "_")
    raw_config = raw_pyproject["tool"]["archlint"]

    return Configuration(
        root_dir=root_dir,
        module_name=module_name,
        docs=get_docs_config(raw_config, root_dir),
        tests=get_tests_config(raw_config, root_dir),
        imports=get_import_config(raw_config, module_name),
        method_order=get_method_order_config(raw_config),
        module_root_dir=root_dir / "src" / module_name,
    )
