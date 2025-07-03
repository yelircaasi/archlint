import re


class Regex:
    CLASS_NAME = re.compile(r"class ([A-Za-z_][A-Za-z_0-9]+)[:\(]")
    CLASS_TEXT = re.compile(
        r"class [A-Za-z_][^\n]+:.+?\n\n\n|class [A-Za-z_][^\n]+:.+?$", re.DOTALL
    )
    DOC_OBJECT_NAME = re.compile(r"## ::: +[^ ]+\.([A-Za-z_0-9]+)\s")
    DUNDER = re.compile("^__.+?__$")
    FUNCTION_NAME = re.compile(r"(?:^|\n)def ([a-z_][A-Za-z_0-9]+)\(")
    DATACLASS_NAME = re.compile(r"@dataclass\nclass ([A-Za-z_0-9]+):")
    MATCH_NOTHING = re.compile("(?!)")
    METHOD_NAME = re.compile(r"\n    def ([a-z_][A-Za-z_0-9]+)\(")
    SUPER_CLASS = re.compile(r"[A-Z_][_A-Za-z_0-9]+(?=[,\[])")
    TEST_CLASS_NAME = re.compile(r"class ([A-Za-z_][A-Za-z_0-9]+)[:\(]")
    TEST_CLASS_TEXT = re.compile(
        r"class Test[A-Za-z_][^\n]+:.+?\n\n\n|class Test[A-Za-z_][^\n]+:.+?$", re.DOTALL
    )
    TEST_FUNCTION_NAME = re.compile(r"\ndef (test_[A-Za-z_][A-Za-z_0-9]+)\(")
    TEST_METHOD_NAME = re.compile(r"\n    def (test_[A-Za-z_][A-Za-z_0-9]+)\(")

    OVERLOADED_PATTERN = re.compile(r"^_\(|^@[A-Za-z_]+\.register")
    NAME_PATTERN = re.compile(r"def ([^\(]+)")
    CLASS_NAME_PATTERN = re.compile(r"^[_A-Z][^:\(]+")
    OBJECT_IN_MD = re.compile(r"#+ ::: [a-z_][a-z_0-9\.]+\.([A-Za-z_0-9]+)\n")

    INIT = re.compile(r"def __init__", re.DOTALL)
    ABSTRACT_DUNDER = re.compile(r"@abstract.+?def __[^ \n]+__\(", re.DOTALL)
    ABSTRACT_PROPERTY = re.compile(r"@property.+?@abstractmethod", re.DOTALL)
    ABSTRACT_PRIVATE_PROPERTY = re.compile(r"@property.+?@abstractmethod.+?def _", re.DOTALL)
    ABSTRACT_CLASSMETHOD = re.compile(r"@classmethod.+?@abstractmethod", re.DOTALL)
    ABSTRACT_STATIC = re.compile(r"@static.+?@abstractmethod", re.DOTALL)
    ABSTRACT_PRIVATE = re.compile(r"@abstractmethod.+?def _", re.DOTALL)
    DUNDER = re.compile(r"def __[a-z0-9_]+?__", re.DOTALL)
    PRIVATE = re.compile(r"def _[^_]", re.DOTALL)
    MANGLED = re.compile(r"def __[^ ]+[^_].\(", re.DOTALL)
    CLASSMETHOD = re.compile(r"@classmethod", re.DOTALL)
    PRIVATE_PROPERTY = re.compile(r"@property.+?def _", re.DOTALL)
    PROPERTY = re.compile(r"@property", re.DOTALL)
    STATIC = re.compile(r"@staticmethod", re.DOTALL)
    FINAL = re.compile(r"@final", re.DOTALL)
    ABSTRACT = re.compile(r"@abstractmethod", re.DOTALL)
