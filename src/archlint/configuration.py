"""
Configuration types and helper functions.

Goal is to perform strict validation and helpful error messages.
"""

import re
import tomllib
from dataclasses import dataclass, field
from functools import partial
from pathlib import Path
from typing import Iterable, Self, TypeVar

from .regexes import Regex
from .utils import (
    assert_bool,
    boolean_merge,
    compile_string_or_bool,
    default_module_name,
    default_module_root_dir,
    get_project_root,
    make_regex,
    prepend_module_name,
)

T = TypeVar("T")


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

    def __repr__(self):
        return str(self)

    def __str__(self) -> str:
        return (
            f"[tool.archlint.docs]\n"
            f'md_dir = "{self.md_dir}"\n'
            f'allow_additional = "{self.allow_additional.pattern}"\n'
            f'ignore = "{self.ignore.pattern}"\n'
            f'file_per_directory = "{self.file_per_directory.pattern}"\n'
            f'file_per_class = "{self.file_per_class.pattern}"\n'
            f"replace_double_underscore = {str(self.replace_double_underscore).lower()}"
        )

    def __eq__(self, other) -> bool:
        if isinstance(other, DocsConfig):
            return other.__dict__ == self.__dict__
        return False

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
        raw = boolean_merge(DEFAULTS, raw_pyproject_docs)
        return cls().merge(
            md_dir=Path(raw["md_dir"]),
            allow_additional=compile_string_or_bool(raw["allow_additional"]),
            ignore=make_regex(raw["ignore"]),
            file_per_directory=make_regex(raw["file_per_directory"]),
            file_per_class=make_regex(raw["file_per_class"]),
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


class ImportInfo:
    def __init__(
        self,
        *,
        is_internal: bool,
        allowed: dict[str, set[str]] | None = None,
        disallowed: dict[str, set[str]] | None = None,
        module_name: str | None = None,
    ):
        def identity(x: T) -> T:
            return x

        prepend_name = (
            partial(prepend_module_name, module_name=module_name) if module_name else identity
        )

        if is_internal:

            def fix_names(d: dict[str, set[str]]) -> dict[str, set[str]]:
                return {prepend_name(k): set(map(prepend_name, v)) for k, v in d.items()}

        else:

            def fix_names(d: dict[str, set[str]]) -> dict[str, set[str]]:
                return {prepend_name(k): set(v) for k, v in d.items()}

        self.is_internal = is_internal
        self.allowed = fix_names(allowed or {})
        self.disallowed = fix_names(disallowed or {})

    def __repr__(self):
        return str(self)

    def __eq__(self, other) -> bool:
        if isinstance(other, ImportInfo):
            return other.__dict__ == self.__dict__
        return False

    def __str__(self) -> str:
        def display_dict(d: dict[str, set[str]]) -> str:
            return "\n".join(
                [f'"{k}" = {str(sorted(v)).replace("'", '"')}' for k, v in sorted(d.items())]
            )

        int_ext = "internal" if self.is_internal else "external"
        allowed = f"allowed]\n{display_dict(self.allowed)}" if self.allowed else ""
        disallowed = f"disallowed]\n{display_dict(self.disallowed)}" if self.disallowed else ""
        if not (self.allowed or self.disallowed):
            return ""
        return f"[tool.archlint.imports.{int_ext}_{allowed or disallowed}"

    def ensure_xor(self) -> None:
        if self.allowed and self.disallowed:
            raise ValueError("Only one of 'allowed' and 'disallowed' may be specified for imports.")


class ImportsConfig:
    def __init__(
        self,
        internal_allowed_everywhere: set[str] | None = None,
        external_allowed_everywhere: set[str] | None = None,
        internal: ImportInfo | None = None,
        external: ImportInfo | None = None,
        grimp_cache: str = ".grimp_cache",
        module_name: str | None = None,
    ):
        self._module_name = module_name or default_module_name()

        self.internal_allowed_everywhere = set(
            map(self._fixer, internal_allowed_everywhere or set())
        )
        self.external_allowed_everywhere = set(external_allowed_everywhere or set())
        self.internal: ImportInfo = internal or ImportInfo(is_internal=True)
        self.external: ImportInfo = external or ImportInfo(is_internal=False)
        self.grimp_cache = grimp_cache

        self._check_conflicts()

    def __repr__(self):
        return str(self)

    def __str__(self) -> str:
        iae = str(sorted(self.internal_allowed_everywhere)).replace("'", '"')
        eae = str(sorted(self.external_allowed_everywhere)).replace("'", '"')
        return (
            f"[tool.archlint.imports]\n"
            f"internal_allowed_everywhere = {iae}\n"
            f"external_allowed_everywhere = {eae}\n"
            f'grimp_cache = "{self.grimp_cache}"\n\n'
            f"{self.internal}\n\n"
            f"{self.external}"
        ).strip("\n")

    def __eq__(self, other) -> bool:
        if isinstance(other, ImportsConfig):
            return other.__dict__ == self.__dict__
        return False

    @classmethod
    def from_dict(cls, raw_icfg: dict, module_name: str | None = None) -> Self:
        module_name = module_name or default_module_name()

        return cls().merge(
            internal_allowed_everywhere=raw_icfg.get("internal_allowed_everywhere", []),
            external_allowed_everywhere=raw_icfg.get("external_allowed_everywhere", []),
            internal=ImportInfo(
                is_internal=True,
                module_name=module_name,
                allowed=raw_icfg.get("internal_allowed", {}),
                disallowed=raw_icfg.get("internal_disallowed", {}),
            ),
            external=ImportInfo(
                is_internal=False,
                module_name=module_name,
                allowed=raw_icfg.get("external_allowed", {}),
                disallowed=raw_icfg.get("external_disallowed", {}),
            ),
            grimp_cache=raw_icfg.get("grimp_cache", ".grimp_cache"),
        )

    def merge(
        self,
        *,
        internal_allowed_everywhere: Iterable[str] | None = None,
        external_allowed_everywhere: Iterable[str] | None = None,
        internal: ImportInfo | None = None,
        external: ImportInfo | None = None,
        grimp_cache: str | None = None,
    ) -> Self:
        self.internal_allowed_everywhere = set(
            map(self._fixer, internal_allowed_everywhere or self.internal_allowed_everywhere)
        )
        self.external_allowed_everywhere = set(
            external_allowed_everywhere or self.external_allowed_everywhere
        )
        self.internal = internal or self.internal
        self.external = external or self.external
        self.grimp_cache = grimp_cache or self.grimp_cache

        self._check_conflicts()
        return self

    def _fixer(self, name: str) -> str:
        return prepend_module_name(name, module_name=self._module_name)

    def _check_conflicts(self) -> None:
        self.internal.ensure_xor()
        self.external.ensure_xor()


BUILTINS = (
    (Regex.methods.INIT, 0.0),
    (Regex.methods.ABSTRACT_PROPERTY, 1.0),
    (Regex.methods.PROPERTY, 2.0),
    (Regex.methods.ABSTRACT_PRIVATE_PROPERTY, 3.0),
    (Regex.methods.PRIVATE_PROPERTY, 4.0),
    (Regex.methods.ABSTRACT_DUNDER, 5.0),
    (Regex.methods.DUNDER, 6.0),
    (Regex.methods.ABSTRACT_CLASSMETHOD, 7.0),
    (Regex.methods.CLASSMETHOD, 8.0),
    (Regex.methods.ABSTRACT, 9.0),
    (Regex.methods.FINAL, 11.0),
    (Regex.methods.ABSTRACT_STATIC, 12.0),
    (Regex.methods.STATIC, 13.0),
    (Regex.methods.ABSTRACT_PRIVATE, 14.0),
    (Regex.methods.PRIVATE, 15.0),
    (Regex.methods.MANGLED, 16.0),
)

BUILTINS_NAME_DICT = {
    Regex.methods.INIT: "init",
    Regex.methods.ABSTRACT_DUNDER: "abstract_dunder",
    Regex.methods.ABSTRACT_PROPERTY: "abstract_property",
    Regex.methods.ABSTRACT_PRIVATE_PROPERTY: "abstract_private_property",
    Regex.methods.ABSTRACT_CLASSMETHOD: "abstract_classmethod",
    Regex.methods.ABSTRACT_STATIC: "abstract_static",
    Regex.methods.ABSTRACT_PRIVATE: "abstract_private",
    Regex.methods.DUNDER: "dunder",
    Regex.methods.PRIVATE: "private",
    Regex.methods.MANGLED: "mangled",
    Regex.methods.CLASSMETHOD: "classmethod",
    Regex.methods.PRIVATE_PROPERTY: "private_property",
    Regex.methods.PROPERTY: "property",
    Regex.methods.STATIC: "static",
    Regex.methods.FINAL: "final",
    Regex.methods.ABSTRACT: "abstract",
}


@dataclass
class MethodsConfig:
    ordering: tuple[tuple[re.Pattern, float], ...] = BUILTINS
    normal: float = 99.0
    # custom: tuple[tuple[re.Pattern, float], ...] = tuple()

    def __repr__(self):
        return str(self)

    def __str__(self) -> str:
        ordering_dict = dict(self.ordering)
        builtin_lines = [
            (name, float(ordering_dict[expr])) for expr, name in BUILTINS_NAME_DICT.items()
        ]
        builtins = "\n".join(
            f"{name} = {number}" for name, number in sorted(builtin_lines, key=lambda p: p[1])
        )
        custom = "\n".join(
            (
                f"{expr.pattern} = {value}"
                for expr, value in self.ordering
                if expr not in BUILTINS_NAME_DICT
            )
        )
        builtins_toml = f"[tool.archlint.methods.builtins_order]\n{builtins}"
        if custom:
            return f"{builtins_toml}\n\n[tool.archlint.methods.custom_order]\n{custom}"
        return builtins_toml

    def __eq__(self, other) -> bool:
        if isinstance(other, MethodsConfig):
            return other.__dict__ == self.__dict__
        return False

    @classmethod
    def from_dict(cls, pyproject_methods_config: dict) -> Self:
        DEFAULT_VALUE = 99.0

        custom_mapping = pyproject_methods_config.get("custom_order", {})
        custom = [(make_regex(k), float(v)) for k, v in custom_mapping.items()]
        builtins_mapping = pyproject_methods_config.get("builtins_order", {})
        predefined = [
            (regexpr, float(builtins_mapping.get(BUILTINS_NAME_DICT[regexpr], DEFAULT_VALUE)))
            for regexpr, _ in BUILTINS
        ]

        return cls().merge(
            ordering=tuple(custom + predefined), normal=builtins_mapping.get("normal", 99.0)
        )

    def merge(
        self,
        *,
        ordering: tuple[tuple[re.Pattern, float], ...] | None = None,
        normal: float | None = None,
    ) -> Self:
        self.ordering = ordering or self.ordering
        self.normal = self.normal if (normal is None) else normal

        return self


@dataclass
class UnitTestsConfig:
    unit_dir: Path = field(default=Path("tests/unit"))
    use_filename_suffix: bool = field(default=True)
    allow_additional: re.Pattern = field(default=Regex.MATCH_NOTHING)
    ignore: re.Pattern = field(default=Regex.MATCH_NOTHING)
    file_per_class: re.Pattern = field(default=Regex.MATCH_NOTHING)
    file_per_directory: re.Pattern = field(default=Regex.MATCH_NOTHING)
    function_per_class: re.Pattern = field(default=Regex.MATCH_NOTHING)
    replace_double_underscore: bool = field(default=False)

    def __repr__(self):
        return str(self)

    def __str__(self) -> str:
        return (
            f"[tool.archlint.tests]\n"
            f'unit_dir = "{self.unit_dir}"\n'
            f"use_filename_suffix = {str(self.use_filename_suffix).lower()}\n"
            f'allow_additional = "{self.allow_additional.pattern}"\n'
            f'ignore = "{self.ignore.pattern}"\n'
            f'file_per_directory = "{self.file_per_directory.pattern}"\n'
            f'file_per_class = "{self.file_per_class.pattern}"\n'
            f'function_per_class = "{self.function_per_class.pattern}"\n'
            f"replace_double_underscore = {str(self.replace_double_underscore).lower()}"
        )

    def __eq__(self, other) -> bool:
        if isinstance(other, UnitTestsConfig):
            return other.__dict__ == self.__dict__
        return False

    @classmethod
    def from_dict(cls, pyproject_archlint_tests: dict) -> Self:
        DEFAULTS = {
            "unit_dir": "tests/unit",
            "use_filename_suffix": True,
            "allow_additional": False,
            "ignore": "",
            "file_per_class": "",
            "file_per_directory": "",
            "function_per_class": "",
            "replace_double_underscore": False,
        }
        raw = boolean_merge(DEFAULTS, pyproject_archlint_tests)
        return cls().merge(
            unit_dir=Path(raw["unit_dir"]),
            use_filename_suffix=assert_bool(raw["use_filename_suffix"]),
            allow_additional=compile_string_or_bool(raw["allow_additional"]),
            ignore=make_regex(raw["ignore"]),
            file_per_class=make_regex(raw["file_per_class"]),
            file_per_directory=make_regex(raw["file_per_directory"]),
            function_per_class=make_regex(raw["function_per_class"]),
            replace_double_underscore=assert_bool(raw["replace_double_underscore"]),
        )

    def merge(
        self,
        *,
        unit_dir: Path | None = None,
        use_filename_suffix: bool | None = None,
        allow_additional: re.Pattern | None = None,
        ignore: re.Pattern | None = None,
        file_per_class: re.Pattern | None = None,
        file_per_directory: re.Pattern | None = None,
        function_per_class: re.Pattern | None = None,
        replace_double_underscore: bool | None = None,
    ) -> Self:
        self.unit_dir = unit_dir or self.unit_dir
        self.use_filename_suffix = use_filename_suffix or self.use_filename_suffix
        self.allow_additional = allow_additional or self.allow_additional
        self.ignore = ignore or self.ignore
        self.file_per_class = file_per_class or self.file_per_class
        self.file_per_directory = file_per_directory or self.file_per_directory
        self.function_per_class = function_per_class or self.function_per_class
        self.replace_double_underscore = replace_double_underscore or self.replace_double_underscore

        return self


@dataclass
class Configuration:
    root_dir: Path = field(default_factory=Path.cwd)
    module_name: str = field(default_factory=default_module_name)
    module_root_dir: Path = field(default_factory=default_module_root_dir)
    docs: DocsConfig = field(default_factory=DocsConfig)
    imports: ImportsConfig = field(default_factory=ImportsConfig)
    methods: MethodsConfig = field(default_factory=MethodsConfig)
    tests: UnitTestsConfig = field(default_factory=UnitTestsConfig)

    def __repr__(self):
        return str(self)

    def __str__(self) -> str:
        return (  # TODO
            f"[tool.archlint]\n"
            f'root_dir = "."\n'
            f'module_name = "{self.module_name}"\n'
            f'module_root_dir = "{self.module_root_dir}"\n\n'
            f"{self.docs}\n\n"
            f"{self.imports}\n\n"
            f"{self.methods}\n\n"
            f"{self.tests}"
        )

    def __eq__(self, other) -> bool:
        if isinstance(other, Configuration):
            return other.__dict__ == self.__dict__
        return False

    @classmethod
    def read(cls, explicitly_passed: str | Path | None = None) -> Self:
        root_dir = get_project_root()
        file_path = Path(explicitly_passed or root_dir / "pyproject.toml")
        raw_dict = tomllib.loads(file_path.read_text())
        module_name = (
            raw_dict["project"]["name"].replace("-", "_")
            if "project" in raw_dict
            else default_module_name()
        )
        return cls.from_dict(raw_dict["tool"]["archlint"], module_name, root_dir)

    @classmethod
    def from_dict(
        cls,
        raw_config: dict,
        module_name: str | None = None,
        project_root: Path | None = None,
    ) -> Self:
        root_dir: Path = project_root or get_project_root()
        module_root_dir = Path(
            raw_config.get("module_root_dir", root_dir / "src" / (module_name or ""))
        )
        if module_root_dir.is_absolute():
            module_root_dir = module_root_dir.relative_to(root_dir)

        return cls().merge(
            root_dir=root_dir,
            module_root_dir=module_root_dir,
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
