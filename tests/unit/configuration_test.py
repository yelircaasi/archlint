import re
import tomllib
from pathlib import Path

import pytest

from archlint.configuration import (
    Configuration,
    DocsConfig,
    ImportInfo,
    ImportsConfig,
    MethodsConfig,
    UnitTestsConfig,
)

DEFAULT_TOML = """
[tool.archlint]
root_dir = "."
module_name = "archlint"
module_root_dir = "/home/isaac/repos/archlint/src/archlint"

[tool.archlint.docs]
md_dir = "docs/md"
allow_additional = "(?!)"
ignore = "(?!)"
file_per_directory = "(?!)"
file_per_class = "(?!)"
replace_double_underscore = false

[tool.archlint.imports]
internal_allowed_everywhere = []
external_allowed_everywhere = []
grimp_cache = ".grimp_cache"

[tool.archlint.methods.builtins_order]
init = 0.0
abstract_property = 1.0
property = 2.0
abstract_private_property = 3.0
private_property = 4.0
abstract_dunder = 5.0
dunder = 6.0
abstract_classmethod = 7.0
classmethod = 8.0
abstract = 9.0
final = 11.0
abstract_static = 12.0
static = 13.0
abstract_private = 14.0
private = 15.0
mangled = 16.0

[tool.archlint.tests]
unit_dir = "tests/unit"
use_filename_suffix = true
allow_additional = "(?!)"
ignore = "(?!)"
file_per_directory = "(?!)"
file_per_class = "(?!)"
function_per_class = "(?!)"
replace_double_underscore = false
""".strip()

OLD_DEFAULT_TOML = """
[tool.archlint]
project_root = "."

[tool.archlint.docs]
md_dir = "docs/md"
allow_additional = false
ignore = ":_[A-Z]"
file_per_class = ""
file_per_directory = "utils"
keep_double_underscore = true

[tool.archlint.imports]
primitive_modules = ["regexes"]
external_allowed_everywhere = [
    "collections",
    "os",
    "pathlib",
    "re",
    "sys",
    "typing",
]
internal_allowed_everywhere = ["utils"]

[tool.archlint.imports.disallowed.internal]

[tool.archlint.imports.disallowed.external]

[tool.archlint.methods]
init = 0
abstract_property = 1
property = 2
abstract_private_property = 3
private_property = 4
abstract_dunder = 5
dunder = 6
abstract_classmethod = 7
classmethod = 8
abstract = 9
normal = 10
final = 11
abstract_static = 12
static = 13
abstract_private = 14
private = 15
mangled = 16

[tool.archlint.methods.regex]


[tool.archlint.tests]
unit_dir = "tests/unit"
use_filename_suffix = true
allow_additional = false
ignore = "_[A-Za-z]|__get_pydantic_core_schema__"
file_per_class = ""
file_per_directory = ""
function_per_class = ""
keep_double_underscore = true
""".strip()

CUSTOM_TOML = """
[tool.archlint]
project_root = "."

[tool.archlint.docs]
allow_additional = false
file_per_class = ""
file_per_directory = "utils"
ignore = ":_[A-Z]"
keep_double_underscore = true
md_dir = "docs/md"

[tool.archlint.imports]
primitive_modules = ["regexes"]
external_allowed_everywhere = [
    "collections",
    "os",
    "pathlib",
    "re",
    "sys",
    "typing",
]
internal_allowed_everywhere = ["utils"]

[tool.archlint.imports.disallowed.internal]

[tool.scripts.imports.disallowed.external]

[tool.archlint.methods.builtins_order]
init = 0
abstract_property = 1
property = 2
abstract_private_property = 3
private_property = 4
abstract_dunder = 5
dunder = 6
abstract_classmethod = 7
classmethod = 8
abstract = 9
normal = 10
final = 11
abstract_static = 12
static = 13
abstract_private = 14
private = 15
mangled = 16

[tool.archlint.methods.custom_order]
random_example = 4.5

[tool.archlint.tests]
unit_dir = "tests/unit"
use_filename_suffix = true
allow_additional = false
ignore = "_[A-Za-z]|__get_pydantic_core_schema__"
file_per_class = ""
file_per_directory = ""
function_per_class = ""
keep_double_underscore = true
""".strip()

"""
default = DocsConfig()
export = str(default)
reimport = tomllib.loads(export)["tool"]["archlint"]["docs"]
assert str(default) == str(DocsConfig.from_dict(reimport))

default = ImportsConfig()
export = str(default)
print(export)
reimport = tomllib.loads(export)["tool"]["archlint"]["imports"]
assert str(default) == str(ImportsConfig.from_dict(reimport))

default = MethodsConfig()
export = str(default)
print(export)
reimport = tomllib.loads(export)["tool"]["archlint"]["methods"]
assert str(default) == str(MethodsConfig.from_dict(reimport))

default = UnitTestsConfig()
export = str(default)
print(export)
reimport = tomllib.loads(export)["tool"]["archlint"]["tests"]
assert str(default) == str(UnitTestsConfig.from_dict(reimport))

default = Configuration()
export = str(default)
print(export)
reimport = tomllib.loads(export)["tool"]["archlint"]
assert str(default) == str(Configuration.from_dict(reimport))
"""


class TestDocsConfig:
    default = DocsConfig()

    def test_dunder_str(self):
        export = str(self.default)
        reimport = tomllib.loads(export)["tool"]["archlint"]["docs"]
        assert str(self.default) == str(DocsConfig.from_dict(reimport))

    def test_from_dict(self):
        default = DocsConfig()
        from_default_toml = DocsConfig.from_dict(
            tomllib.loads(DEFAULT_TOML)["tool"]["archlint"]["docs"]
        )
        assert default == from_default_toml

        custom = DocsConfig(
            md_dir=Path("docs/md"),
            allow_additional=re.compile(r"(?!)"),
            ignore=re.compile(r":_[A-Z]"),
            file_per_class=re.compile(r"(?!)"),
            file_per_directory=re.compile(r"utils"),
            replace_double_underscore=False,
        )
        from_custom_toml = DocsConfig.from_dict(
            tomllib.loads(CUSTOM_TOML)["tool"]["archlint"]["docs"]
        )
        assert custom == from_custom_toml

    def test_merge(self):
        default = DocsConfig()
        other = DocsConfig(file_per_class=re.compile(r"Custom"))
        assert default.merge(file_per_class=re.compile(r"Custom")) == other


class TestImportInfo:
    def test_dunder_str(self):
        with_allowed = ImportInfo(is_internal=True, allowed={"a": {"b", "c"}})
        with_disallowed = ImportInfo(is_internal=False, disallowed={"a": {"b", "c"}})

        assert str(with_allowed) == ('[tool.archlint.imports.internal_allowed]\n"a" = ["b", "c"]')
        assert str(with_disallowed) == (
            '[tool.archlint.imports.external_disallowed]\n"a" = ["b", "c"]'
        )

    def test_ensure_xor(self):
        with pytest.raises(
            ValueError, match="Only one of 'allowed' and 'disallowed' may be specified for imports."
        ):
            ii = ImportInfo(
                is_internal=True, allowed={"a": {"b", "c"}}, disallowed={"a": {"b", "c"}}
            )
            ii.ensure_xor()


class TestImportsConfig:
    default = ImportsConfig()

    def test_dunder_str(self):
        export = str(self.default)
        reimport = tomllib.loads(export)["tool"]["archlint"]["imports"]
        assert str(self.default) == str(ImportsConfig.from_dict(reimport))

    def test_from_dict(self):
        default = ImportsConfig()
        raw_dict = tomllib.loads(DEFAULT_TOML)["tool"]["archlint"]["imports"]
        from_default_toml = ImportsConfig.from_dict(raw_dict)
        assert default == from_default_toml

        custom = ImportsConfig(
            internal_allowed_everywhere=["utils"],
            external_allowed_everywhere=["collections", "os", "pathlib", "re", "sys", "typing"],
        )
        raw_dict = tomllib.loads(CUSTOM_TOML)["tool"]["archlint"]["imports"]
        from_custom_toml = ImportsConfig.from_dict(raw_dict)
        assert custom == from_custom_toml

    def test_merge(self):
        default = ImportsConfig()
        other = ImportsConfig(internal_allowed_everywhere={"archlint.random"})
        assert default.merge(internal_allowed_everywhere={"archlint.random"}) == other

        default = ImportsConfig()
        other = ImportsConfig(internal_allowed_everywhere={"archlint.random"})
        assert default.merge(internal_allowed_everywhere={"random"}) == other

    def test_fixer(self):
        default = ImportsConfig(module_name="hello")
        assert default._fixer("submodule") == "hello.submodule"
        assert default._fixer("hello.submodule") == "hello.submodule"

    def test_check_conflicts(self):
        assert self.default._check_conflicts() is None


class TestMethodsConfig:
    default = MethodsConfig()

    def test_dunder_str(self):
        export = str(self.default)
        reimport = tomllib.loads(export)["tool"]["archlint"]["methods"]
        assert str(self.default) == str(MethodsConfig.from_dict(reimport))

    def test_from_dict(self):
        default = MethodsConfig()
        raw_dict = tomllib.loads(DEFAULT_TOML)["tool"]["archlint"]["methods"]
        from_default_toml = MethodsConfig.from_dict(raw_dict)
        assert default == from_default_toml

        custom = MethodsConfig(
            ordering=(
                (re.compile(r"random_example", re.UNICODE), 4.5),
                (re.compile(r"def __init__", re.DOTALL | re.UNICODE), 0.0),
                (re.compile(r"@property.+?@abstractmethod", re.DOTALL | re.UNICODE), 1.0),
                (re.compile(r"@property", re.DOTALL | re.UNICODE), 2.0),
                (re.compile(r"@property.+?@abstractmethod.+?def _", re.DOTALL | re.UNICODE), 3.0),
                (re.compile(r"@property.+?def _", re.DOTALL | re.UNICODE), 4.0),
                (re.compile(r"@abstract.+?def __[^ \n]+__\(", re.DOTALL | re.UNICODE), 5.0),
                (re.compile(r"def __[a-z0-9_]+?__", re.DOTALL | re.UNICODE), 6.0),
                (re.compile(r"@classmethod.+?@abstractmethod", re.DOTALL | re.UNICODE), 7.0),
                (re.compile(r"@classmethod", re.DOTALL | re.UNICODE), 8.0),
                (re.compile(r"@abstractmethod", re.DOTALL | re.UNICODE), 9.0),
                (re.compile(r"@final", re.DOTALL | re.UNICODE), 11.0),
                (re.compile(r"@static.+?@abstractmethod", re.DOTALL | re.UNICODE), 12.0),
                (re.compile(r"@staticmethod", re.DOTALL | re.UNICODE), 13.0),
                (re.compile(r"@abstractmethod.+?def _", re.DOTALL | re.UNICODE), 14.0),
                (re.compile(r"def _[^_]", re.DOTALL | re.UNICODE), 15.0),
                (re.compile(r"def __[^ ]+[^_].\(", re.DOTALL | re.UNICODE), 16.0),
            )
        )
        raw_dict = tomllib.loads(CUSTOM_TOML)["tool"]["archlint"]["methods"]
        from_custom_toml = MethodsConfig.from_dict(raw_dict)
        assert custom == from_custom_toml

    def test_merge(self):
        custom_ordering = (
            (re.compile(r"random_example", re.UNICODE), 4.5),
            (re.compile(r"def __init__", re.DOTALL | re.UNICODE), 0.0),
            (re.compile(r"@property.+?@abstractmethod", re.DOTALL | re.UNICODE), 1.0),
        )
        default = MethodsConfig()
        other = MethodsConfig(ordering=custom_ordering)
        assert default.merge(ordering=custom_ordering) == other


class TestUnitTestsConfig:
    default = UnitTestsConfig()

    def test_dunder_str(self):
        export = str(self.default)
        reimport = tomllib.loads(export)["tool"]["archlint"]["tests"]
        assert str(self.default) == str(UnitTestsConfig.from_dict(reimport))

    def test_from_dict(self):
        default = UnitTestsConfig()
        from_default_toml = UnitTestsConfig.from_dict(
            tomllib.loads(DEFAULT_TOML)["tool"]["archlint"]["tests"]
        )
        assert default == from_default_toml

        custom = UnitTestsConfig(ignore=re.compile("_[A-Za-z]|__get_pydantic_core_schema__"))
        raw_dict = tomllib.loads(CUSTOM_TOML)["tool"]["archlint"]["tests"]
        from_custom_toml = UnitTestsConfig.from_dict(raw_dict)
        assert custom == from_custom_toml

    def test_merge(self):
        default = UnitTestsConfig()
        other = UnitTestsConfig(file_per_class=re.compile(r"Custom"))
        assert default.merge(file_per_class=re.compile(r"Custom")) == other


class TestConfiguration:
    default = Configuration()

    def test_dunder_str(self):
        export = str(self.default)
        reimport = tomllib.loads(export)["tool"]["archlint"]
        reimported = Configuration.from_dict(reimport)
        assert str(self.default) == str(reimported)

    def test_read(self):
        default_toml = Path(__file__).parent.parent / "_data/default.toml"
        assert Configuration.read(explicitly_passed=default_toml) == self.default

    def test_from_dict(self):
        default = Configuration()
        from_default_toml = Configuration.from_dict(tomllib.loads(DEFAULT_TOML)["tool"]["archlint"])
        assert default == from_default_toml

        # custom = Configuration(
        #     root_dir="",
        #     module_name="",
        #     docs=DocsConfig(),
        #     tests=UnitTestsConfig(),
        #     methods=MethodsConfig(),
        #     imports=ImportsConfig(),
        # )
        # from_custom_toml = Configuration.from_dict(tomllib.loads(CUSTOM_TOML)["tool"]["archlint"])
        # assert custom == from_custom_toml

    def test_merge(self):
        default = Configuration()
        other = Configuration(root_dir="some/root")
        assert default.merge(root_dir="some/root") == other
