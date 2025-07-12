# Configuration

Configuration is done in `pyproject.toml`, located in the project's top-level directory.

## Default Configuration

pyproject.toml

```toml
[tool.archlint]
project_root = "."

[tool.archlint.docs]
allow_additional = false
file_per_class = ""
file_per_directory = "utils"
ignore = ":_[A-Z]"
keep_double_underscore = true
md_dir = "docs/md/api"

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
```

## Configuration for `archlint` Source Code

pyproject.toml

```toml
[tool.archlint]
source_directory = "src"

[tool.archlint.docs]
md_dir = "docs/md/api"
allow_additional = false
ignore = "exceptions.py|:_[A-Z]"
file_per_class = ""
file_per_directory = "linus|guido|grace|utils"
replace_double_underscore = false

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
internal_allowed_everywhere = ["regexes"]

[tool.archlint.imports.disallowed.internal]
utils = ["utils"]

[tool.scripts.imports.disallowed.external]
utils = ["pydantic"]

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

[tool.archlint.tests]
unit_dir = "tests/unit"
use_filename_suffix = true
allow_additional = false
ignore = ":test__[A-Z]|__init__$|_abcs|exceptions|__get_pydantic_core_schema__"
file_per_class = ""
file_per_directory = "linus|guido|grace|utils"
function_per_class = ""
replace_double_underscore = true

```

## Example Custom Configuration

pyproject.toml

```toml
[tool.archlint.methods.custom_order]
"@model_validator|model_validate" = 0
"_pydantic_" = 0.01
" adapter(" = 0.011
"@field_validator" = 0.1
"model_serializ|model_dump" = 0.00001
"@field_serializer" = 0.3
"__call__" = 0.99
"check_.+" = 9
" read[^ ]+(" = 3.98
" write[^ ]+(" = 3.99
"[^_][a-z_]+_hook$" = 9
```

## Configuration Options

Note: All options annotated with '`#!jinja {{ARCHLINT_REGEX}}`' are TOML strings which must
support compilation to valid regular expressions via the Python Standard Library's `#!python re.compile`. However, unlike regular expressions, if the string is empty, it will be treated by `archlint` as matching nothing. Alternatively, a list of strings may be passed and they will be joined with `|` before compilation as a regular expression.

For example, the following are equivalent:

- `#!toml file_per_class = ["match_this", "or_this"]`
- `#!toml file_per_class = "match_this|or_this"`

Note that object paths are of the form `#!jinja "{{path}}:{{class_name}}.{{method_name}}"` or `#!jinja "{{path}}:{{function_name}}"`, so regexes can be written accordingly.

### `#!toml [tool.archlint]` (global configs for `archlint`)

- `#!toml checks`: `array[string]`: default `#!toml ["docs", "imports", "methods", "tests"]`
- `#!toml source_root`: `string`: default `#!toml "src"`
- `#!toml module_name`: `string`: default derived from `pyproject.toml`

### `#!toml [tool.archlint.docs]`

- `#!toml md_dir`: `string`: default `#!toml "docs/md/api"`:

    Directory in which the documentation markdown files reside.

- `#!toml allow_additional`: `#!toml true` | `#!toml false` | `#!jinja {{ARCHLINT_REGEX}}`:

    which 'unexpected' documentation objects (i.e. objects in the documentation lacking a direct correspondance in the source code) should be allowed.

- `#!toml ignore`: `ARCHLINT_REGEX`: default `#!toml ":_[A-Z]"`:

    Pattern to match all source paths and objects which are to not required to have a corresponding documentation entry.

- `#!toml file_per_class`: `ARCHLINT_REGEX`: default `#!toml ""`:

    Pattern to match all classes which are to receive their own documentation file.

- `#!toml file_per_directory`: `ARCHLINT_REGEX`: default `#!toml ""`:

    Pattern to match all directories which are to be compressed into a single documentation file.

### `#!toml [tool.archlint.imports]`

For each of `#!toml internal` and `#!toml external`, only one of `#!toml allowed` and
`#!toml disallowed` should be specified.
Analogously to the behavior of firewall rules, specifying allowed
imports will disallow everything not explicitly listed. Conversely, specifying disallowed
imports will allow everything not explicitly listed.

If, contrary to these guidelines, both options are specified, `archlint` will emit a warning
and ignore the disallow list.

### `#!toml [tool.archlint.imports.external.allowed]`

`table[string, array[string]]`

- `#!jinja {{IMPORTING_MODULE_NAME}}` `#!toml =` `#!jinja {{IMPORT_NAME_ARRAY}}`

### `#!toml [tool.archlint.imports.external.disallowed]`

`table[string, array[string]]`

- `#!jinja {{IMPORTING_MODULE_NAME}}` `#!toml =` `#!jinja {{IMPORT_NAME_ARRAY}}`

### `#!toml [tool.archlint.imports.internal.allowed]`

`table[string, array[string]]`

- `#!jinja {{IMPORTING_MODULE_NAME}}` `#!toml =` `#!jinja {{IMPORT_NAME_ARRAY}}`

### `#!toml [tool.archlint.imports.internal.disallowed]`

`table[string, array[string]]`

- `#!jinja {{IMPORTING_MODULE_NAME}}` `#!toml =` `#!jinja {{IMPORT_NAME_ARRAY}}`

### `#!toml [tool.archlint.methods]`

- `#!toml normal`: `float`: default `#!toml 999.0`

### `#!toml [tool.archlint.methods.builtins_order]`

While these fields have default values, they should be included for readability if any custom patterns are passed in the next section, as ordering is purely relative.

- `#!toml init =` `#!jinja {{ORDERING_FLOAT}}`: default `#!toml 0.0`
- `#!toml abstract_property =` `#!jinja {{ORDERING_FLOAT}}`: default `#!toml 1.0`
- `#!toml property =` `#!jinja {{ORDERING_FLOAT}}`: default `#!toml 2.0`
- `#!toml abstract_private_property =` `#!jinja {{ORDERING_FLOAT}}`: default `#!toml 3.0`
- `#!toml private_property =` `#!jinja {{ORDERING_FLOAT}}`: default `#!toml 4.0`
- `#!toml abstract_dunder =` `#!jinja {{ORDERING_FLOAT}}`: default `#!toml 5.0`
- `#!toml dunder =` `#!jinja {{ORDERING_FLOAT}}`: default `#!toml 6.0`
- `#!toml abstract_classmethod =` `#!jinja {{ORDERING_FLOAT}}`: default `#!toml 7.0`
- `#!toml classmethod =` `#!jinja {{ORDERING_FLOAT}}`: default `#!toml 8.0`
- `#!toml abstract =` `#!jinja {{ORDERING_FLOAT}}`: default `#!toml 9.0`
- `#!toml normal =` `#!jinja {{ORDERING_FLOAT}}`: default `#!toml 10.0`
- `#!toml final =` `#!jinja {{ORDERING_FLOAT}}`: default `#!toml 11.0`
- `#!toml abstract_static =` `#!jinja {{ORDERING_FLOAT}}`: default `#!toml 12.0`
- `#!toml static =` `#!jinja {{ORDERING_FLOAT}}`: default `#!toml 13.0`
- `#!toml abstract_private =` `#!jinja {{ORDERING_FLOAT}}`: default `#!toml 14.0`
- `#!toml private =` `#!jinja {{ORDERING_FLOAT}}`: default `#!toml 15.0`
- `#!toml mangled =` `#!jinja {{ORDERING_FLOAT}}`: default `#!toml 16.0`

### `#!toml [tool.archlint.methods.custom_order]`

A mapping assigning numerical values to regular expressions for purposes of method order enforcement.

The order of regular expressions matters here, because the value corresponding to the first matching regular expression is used. Thus, when multiple regular expressions can match the same method, the narrower expression should precede the broader expression. In accordance with this
principle of "narrow before broad", custom regular expressions are matched against before
the built-in regular expressions, which are mapped to the ordinal values declared in the
previous section.

- `#!jinja {{ARCHLINT_REGEX}}` `#!toml =` `#!jinja {{ORDERING_FLOAT}}`

### `#!toml [tool.archlint.tests]`

- `#!toml unit_dir`: `string`: default `#!toml "tests/unit"`

    Directory in which the unit tests reside.

- `#!toml use_filename_suffix`: `boolean`: default `#!toml true`:

    Whether test files use the naming convention `*_test.py`; if false, then `test_*`.

- `#!toml allow_additional`: `#!toml true` | `#!toml false` | `#!jinja {{ARCHLINT_REGEX}}`:
  default: `#!toml true`

    Which 'unexpected' test objects (i.e. objects in the tests lacking a direct correspondance in the source code) should be allowed; default is to allow all.

- `#!toml ignore`: `ARCHLINT_REGEX`: default: `#!toml ":_[A-Za-z]|__get_pydantic_core_schema__"`

    Pattern to filter out source paths and objects which are to be ignored.

- `#!toml file_per_class`: `ARCHLINT_REGEX`:

    Pattern to match all classes which are to receive their own test file.

- `#!toml file_per_directory`: `ARCHLINT_REGEX`:

    Pattern to match all directories which are to be collapsed into a single test file.

- `#!toml function_per_class`: `ARCHLINT_REGEX`:

    Pattern to match all classes which should be mapped to a test function instead of a test class.

- `#!toml replace_double_underscore`: `boolean`: default `#!toml false`:

    Whether double and triple underscores should be replaced with a single underscore in test file names and test object names. For example a method named `_shuffle` will make `archlint` expect a test method named `test__shuffle` if this is set to `#!toml false` and `test_shuffle` if it is set to `#!toml true`.
