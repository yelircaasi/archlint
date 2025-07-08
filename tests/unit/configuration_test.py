import tomllib

from archlint.configuration import (
    Configuration,
    DocsConfig,
    ImportsConfig,
    MethodsConfig,
    TstsConfig,
    get_config,
    get_docs_config,
    get_imports_config,
    get_methods_config,
    get_tests_config,
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


def test_get_docs_config():
    default = get_docs_config({})
    from_default_toml = get_docs_config(tomllib.loads(DEFAULT_TOML)["tool"]["archlint"]["docs"])
    assert default == from_default_toml

    custom = DocsConfig()  # TODO
    from_custom_toml = get_docs_config(tomllib.loads(CUSTOM_TOML)["tool"]["archlint"]["docs"])
    assert custom == from_custom_toml


def test_get_imports_config():
    default = get_imports_config({})
    from_default_toml = get_imports_config(tomllib.loads(DEFAULT_TOML)["tool"]["archlint"]["imports"])
    assert default == from_default_toml

    custom = ImportsConfig()  # TODO
    from_custom_toml = get_imports_config(tomllib.loads(CUSTOM_TOML)["tool"]["archlint"]["imports"])
    assert custom == from_custom_toml


def test_get_methods_config():
    default = get_methods_config({})
    from_default_toml = get_methods_config(tomllib.loads(DEFAULT_TOML)["tool"]["archlint"]["methods"])
    assert default == from_default_toml

    custom = MethodsConfig()  # TODO
    from_custom_toml = get_methods_config(tomllib.loads(CUSTOM_TOML)["tool"]["archlint"]["methods"])
    assert custom == from_custom_toml


def test_get_tests_config():
    default = get_tests_config({})
    from_default_toml = get_tests_config(tomllib.loads(DEFAULT_TOML)["tool"]["archlint"]["tests"])
    assert default == from_default_toml

    custom = TstsConfig()  # TODO
    from_custom_toml = get_tests_config(tomllib.loads(CUSTOM_TOML)["tool"]["archlint"]["tests"])
    assert custom == from_custom_toml


def test_get_config():
    default = get_config({})
    from_default_toml = get_config(tomllib.loads(DEFAULT_TOML)["tool"]["archlint"])
    assert default == from_default_toml

    custom = Configuration()  # TODO
    from_custom_toml = get_config(tomllib.loads(CUSTOM_TOML)["tool"]["archlint"])
    assert custom == from_custom_toml
