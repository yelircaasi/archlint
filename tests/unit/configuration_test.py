import tomllib

from archlint.configuration import (
    Configuration,
    DocsConfig,
    ImportsConfig,
    MethodsConfig,
    UnitTestsConfig,
)

DEFAULT_TOML = """
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
"""

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
"""


class TestDocsConfig:
    def test_merge(self): ...

    def test_from_dict(self):
        default = DocsConfig()
        from_default_toml = DocsConfig.from_dict(tomllib.loads(DEFAULT_TOML)["tool"]["archlint"]["docs"])
        assert default == from_default_toml

        custom = DocsConfig()  # TODO
        from_custom_toml = DocsConfig.from_dict(tomllib.loads(CUSTOM_TOML)["tool"]["archlint"]["docs"])
        assert custom == from_custom_toml


class TestImportsConfig:
    def test_merge(self): ...

    def test_from_dict(self):
        default = ImportsConfig()
        from_default_toml = ImportsConfig.from_dict(tomllib.loads(DEFAULT_TOML)["tool"]["archlint"]["imports"])
        assert default == from_default_toml

        custom = ImportsConfig()  # TODO
        from_custom_toml = ImportsConfig.from_dict(tomllib.loads(CUSTOM_TOML)["tool"]["archlint"]["imports"])
        assert custom == from_custom_toml


class TestMethodsConfig:
    def test_merge(self): ...

    def test_from_dict(self):
        default = MethodsConfig()
        from_default_toml = MethodsConfig.from_dict(tomllib.loads(DEFAULT_TOML)["tool"]["archlint"]["methods"])
        assert default == from_default_toml

        custom = MethodsConfig()  # TODO
        from_custom_toml = MethodsConfig.from_dict(tomllib.loads(CUSTOM_TOML)["tool"]["archlint"]["methods"])
        assert custom == from_custom_toml


class TestUnitTestsConfig:
    def test_merge(self): ...

    def test_from_dict(self):
        default = UnitTestsConfig()
        from_default_toml = UnitTestsConfig.from_dict(tomllib.loads(DEFAULT_TOML)["tool"]["archlint"]["tests"])
        assert default == from_default_toml

        custom = UnitTestsConfig()  # TODO
        from_custom_toml = UnitTestsConfig.from_dict(tomllib.loads(CUSTOM_TOML)["tool"]["archlint"]["tests"])
        assert custom == from_custom_toml


class TestUnitTestsConfig:
    def test_merge(self): ...

    def test_from_dict(self):
        default = Configuration()
        from_default_toml = Configuration.from_dict(tomllib.loads(DEFAULT_TOML)["tool"]["archlint"])
        assert default == from_default_toml

        custom = Configuration()  # TODO
        from_custom_toml = Configuration.from_dict(tomllib.loads(CUSTOM_TOML)["tool"]["archlint"])
        assert custom == from_custom_toml
