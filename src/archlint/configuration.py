"""
Configuration types and helper functions.

Goal is to perform strict validation and helpful error messages.
"""

import re
import tomllib
from dataclasses import dataclass, field
from functools import partial
from pathlib import Path
from typing import Self, cast

from .regexes import Regex
from .utils import (
    assert_bool,
    compile_for_path_segment,
    compile_string_or_bool,
    default_module_name,
    default_module_root_dir,
    get_project_root,
    make_regex,
    prepend_module_name,
)


@dataclass
class DocsConfig:
    md_dir: Path = Path("docs/md")
    """ """

    allow_additional: re.Pattern = Regex.MATCH_NOTHING
    """ Whether/which additional documentation files and objects should be allowed. """

    ignore: re.Pattern = Regex.MATCH_NOTHING
    """
    Regular expression matching any files or objects that should not be included in the
        analysis of documentation structure.
    """

    file_per_class: re.Pattern = Regex.MATCH_NOTHING
    """ Regular expression matching any classes (including path) that should be
        promoted to thir own .md file."""

    file_per_directory: re.Pattern = Regex.MATCH_NOTHING
    """
    Regular expression matching any directories that should be collapsed to
        a single .md file.
    """

    replace_double_underscore: bool = False
    """ Whether """

    @classmethod
    def from_dict(cls, raw_pyproject_docs: dict) -> Self:
        DEFAULTS = {
            "md_dir": "docs/md",
            "allow_additional": False,
            "ignore": "",
            "file_per_directory": "",
            "file_per_class": "",
            "replace_double_underscore": False,
        }
        raw = DEFAULTS | raw_pyproject_docs
        return cls().merge(
            md_dir=Path(raw["md_dir"]).absolute(),
            allow_additional=compile_string_or_bool(raw["allow_additional"]),
            ignore=compile_for_path_segment(raw["ignore"]),
            file_per_directory=compile_for_path_segment(raw["file_per_directory"]),
            file_per_class=compile_for_path_segment(raw["file_per_class"]),
            replace_double_underscore=assert_bool(raw["replace_double_underscore"]),
        )

    def merge(
        self,
        *,
        md_dir: Path | None = None,
        allow_additional: re.Pattern | None = None,
        ignore: re.Pattern | None = None,
        file_per_class: re.Pattern | None = None,
        file_per_directory: re.Pattern | None = None,
        replace_double_underscore: bool | None = None,
    ) -> Self:
        self.md_dir = md_dir or self.md_dir
        self.allow_additional = allow_additional or self.allow_additional
        self.ignore = ignore or self.ignore
        self.file_per_class = file_per_class or self.file_per_class
        self.file_per_directory = file_per_directory or self.file_per_directory
        self.replace_double_underscore = replace_double_underscore or self.replace_double_underscore

        return self


@dataclass
class ImportInfo:
    internal: dict[str, set[str]] = field(default_factory=dict)
    external: dict[str, set[str]] = field(default_factory=dict)


class ImportsConfig:
    def __init__(
        self,
        internal_allowed_everywhere: set[str] | None = None,
        external_allowed_everywhere: set[str] | None = None,
        allowed: ImportInfo | None = None,
        disallowed: ImportInfo | None = None,
        grimp_cache: str = "/tmp/grimp_cache",
    ):
        self.internal_allowed_everywhere = internal_allowed_everywhere or set()
        self.external_allowed_everywhere = external_allowed_everywhere or set()
        self.allowed: ImportInfo = allowed or ImportInfo()
        self.disallowed: ImportInfo = disallowed or ImportInfo()
        self.grimp_cache = grimp_cache

        self._check_conflicts()

    @classmethod
    def from_dict(cls, raw_imports_config: dict, module_name: str | None = None) -> Self:
        def fix_internal(d: dict[str, list[str]], mod_name: str) -> dict[str, set[str]]:
            prepend_name = partial(prepend_module_name, module_name=mod_name)
            return {prepend_name(k): set(map(prepend_name, v)) for k, v in d.items()}

        def fix_external(d: dict[str, list[str]], mod_name: str) -> dict[str, set[str]]:
            return {prepend_module_name(k, mod_name): set(v) for k, v in d.items()}

        module_name = module_name or default_module_name()

        return cls().merge(
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

    def merge(
        self,
        *,
        internal_allowed_everywhere: set[str] | None = None,
        external_allowed_everywhere: set[str] | None = None,
        allowed: ImportInfo | None = None,
        disallowed: ImportInfo | None = None,
        grimp_cache: str | None = None,
    ) -> Self:
        self.internal_allowed_everywhere = (
            internal_allowed_everywhere or self.internal_allowed_everywhere
        )
        self.external_allowed_everywhere = (
            external_allowed_everywhere or self.external_allowed_everywhere
        )
        self.allowed = allowed or self.allowed
        self.disallowed = disallowed or self.disallowed
        self.grimp_cache = grimp_cache or self.grimp_cache

        self._check_conflicts()
        return self

    def _check_conflicts(self) -> None:
        if self.allowed.internal and self.disallowed.internal:
            raise ValueError(
                "Only one of 'allowed' and 'disallowed' may be specified for internal imports."
            )
        if self.allowed.external and self.disallowed.external:
            raise ValueError(
                "Only one of 'allowed' and 'disallowed' may be specified for external imports."
            )


@dataclass
class MethodsConfig:
    normal: float = 99.0
    ordering: tuple[tuple[re.Pattern, float], ...] = tuple()

    @classmethod
    def from_dict(cls, pyproject_methods_config: dict) -> Self:
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

        return cls().merge(
            normal=float(builtins_mapping.get("normal", DEFAULT_VALUE)),
            ordering=tuple(custom + predefined),
        )

    def merge(
        self,
        *,
        normal: float | None = None,
        ordering: tuple[tuple[re.Pattern, float], ...] | None = None,
    ) -> Self:
        self.normal = normal if normal is not None else self.normal
        self.ordering = ordering or self.ordering

        return self


@dataclass
class UnitTestsConfig:
    unit_dir: Path = field(default=Path("tests/unit"))
    allow_additional: re.Pattern = field(default=Regex.MATCH_NOTHING)
    ignore: re.Pattern = field(default=Regex.MATCH_NOTHING)
    file_per_class: re.Pattern = field(default=Regex.MATCH_NOTHING)
    file_per_directory: re.Pattern = field(default=Regex.MATCH_NOTHING)
    function_per_class: re.Pattern = field(default=Regex.MATCH_NOTHING)
    replace_double_underscore: bool = field(default=False)
    use_filename_suffix: bool = field(default=True)

    @classmethod
    def from_dict(cls, pyproject_archlint_tests: dict) -> Self:
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
        return cls().merge(
            unit_dir=Path(raw["unit_dir"]).absolute(),
            allow_additional=compile_string_or_bool(raw["allow_additional"]),
            ignore=compile_for_path_segment(raw["ignore"]),
            file_per_class=compile_for_path_segment(raw["file_per_class"]),
            file_per_directory=compile_for_path_segment(raw["file_per_directory"]),
            function_per_class=compile_for_path_segment(raw["function_per_class"]),
            replace_double_underscore=assert_bool(raw["replace_double_underscore"]),
            use_filename_suffix=assert_bool(raw["use_filename_suffix"]),
        )

    def merge(
        self,
        *,
        unit_dir: Path | None = None,
        allow_additional: re.Pattern | None = None,
        ignore: re.Pattern | None = None,
        file_per_class: re.Pattern | None = None,
        file_per_directory: re.Pattern | None = None,
        function_per_class: re.Pattern | None = None,
        replace_double_underscore: bool | None = None,
        use_filename_suffix: bool | None = None,
    ) -> Self:
        self.unit_dir = unit_dir or self.unit_dir
        self.allow_additional = allow_additional or self.allow_additional
        self.ignore = ignore or self.ignore
        self.file_per_class = file_per_class or self.file_per_class
        self.file_per_directory = file_per_directory or self.file_per_directory
        self.function_per_class = function_per_class or self.function_per_class
        self.replace_double_underscore = replace_double_underscore or self.replace_double_underscore
        self.use_filename_suffix = use_filename_suffix or self.use_filename_suffix

        return self


@dataclass
class Configuration:
    root_dir: Path = field(default_factory=Path.cwd)
    module_name: str = field(default_factory=default_module_name)
    docs: DocsConfig = field(default_factory=DocsConfig)
    tests: UnitTestsConfig = field(default_factory=UnitTestsConfig)
    imports: ImportsConfig = field(default_factory=ImportsConfig)
    methods: MethodsConfig = field(default_factory=MethodsConfig)
    module_root_dir: Path = field(default_factory=default_module_root_dir)

    @classmethod
    def read(cls, explicitly_passed: str | Path | None = None) -> Self:
        root_dir = get_project_root()
        file_path = Path(explicitly_passed or root_dir / "pyproject.toml")
        raw_dict = tomllib.loads(file_path.read_text())
        return cls.from_dict(raw_dict, root_dir)

    @classmethod
    def from_dict(cls, config_dict: dict, project_root: Path | None = None) -> Self:
        root_dir: Path = project_root or get_project_root()
        raw_pyproject: dict = tomllib.loads((root_dir / "pyproject.toml").read_text())
        module_name = raw_pyproject["project"]["name"].replace("-", "_")
        raw_config = raw_pyproject.get("tool", {}).get("archlint", {})

        return cls().merge(
            root_dir=root_dir,
            module_root_dir=root_dir / "src" / module_name,
            module_name=raw_config.get("module_name", module_name),
            docs=DocsConfig.from_dict(raw_config.get("docs", {})),
            imports=ImportsConfig.from_dict(raw_config.get("imports", {}), module_name),
            tests=UnitTestsConfig.from_dict(raw_config.get("tests", {})),
            methods=MethodsConfig.from_dict(raw_config.get("methods", {})),
        )

    def merge(
        self,
        *,
        root_dir: Path | None = None,
        module_name: str | None = None,
        docs: DocsConfig | None = None,
        tests: UnitTestsConfig | None = None,
        imports: ImportsConfig | None = None,
        methods: MethodsConfig | None = None,
        module_root_dir: Path | None = None,
    ) -> Self:
        self.root_dir = root_dir or self.root_dir
        self.module_name = module_name or self.module_name
        self.docs = docs or self.docs
        self.tests = tests or self.tests
        self.imports = imports or self.imports
        self.methods = methods or self.methods
        self.module_root_dir = module_root_dir or self.module_root_dir

        return self
