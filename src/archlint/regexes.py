"""
Collection of regular expression constants used to collect code objects.
"""

import re


class Methods:
    ABSTRACT = re.compile(r"@abstractmethod", re.DOTALL)
    ABSTRACT_CLASSMETHOD = re.compile(r"@classmethod.+?@abstractmethod", re.DOTALL)
    ABSTRACT_DUNDER = re.compile(r"@abstract.+?def __[^ \n]+__\(", re.DOTALL)
    ABSTRACT_PRIVATE = re.compile(r"@abstractmethod.+?def _", re.DOTALL)
    ABSTRACT_PRIVATE_PROPERTY = re.compile(r"@property.+?@abstractmethod.+?def _", re.DOTALL)
    ABSTRACT_PROPERTY = re.compile(r"@property.+?@abstractmethod", re.DOTALL)
    ABSTRACT_STATIC = re.compile(r"@static.+?@abstractmethod", re.DOTALL)
    CLASSMETHOD = re.compile(r"@classmethod", re.DOTALL)
    DUNDER = re.compile(r"def __[a-z0-9_]+?__", re.DOTALL)
    FINAL = re.compile(r"@final", re.DOTALL)
    INIT = re.compile(r"def __init__", re.DOTALL)
    MANGLED = re.compile(r"def __[^ ]+[^_].\(", re.DOTALL)
    PRIVATE = re.compile(r"def _[^_]", re.DOTALL)
    PRIVATE_PROPERTY = re.compile(r"@property.+?def _", re.DOTALL)
    PROPERTY = re.compile(r"@property", re.DOTALL)
    STATIC = re.compile(r"@staticmethod", re.DOTALL)


class Regex:
    CLASS_NAME = re.compile(r"class ([A-Za-z_][A-Za-z_0-9]+)[:\(]")
    DUNDER = re.compile("^__.+?__$")
    FUNCTION_NAME = re.compile(r"(?:^|\n)def ([^\(]+)")
    MATCH_NOTHING = re.compile("(?!)")
    METHOD_NAME = re.compile(r"def ([^\(]+)\(")
    OBJECT_IN_MD = re.compile(r"##+ ::: [a-z_][a-z_0-9\.]+\.([A-Za-z_0-9]+)\n")
    OBJECT_TEXT = re.compile(
        (
            r"class [A-Za-z_][^\n]+:.+?\n\n\n|class [A-Za-z_][^\n]+:.+?$"
            r"|(?<=\n)@|(?<=\n)def [^\n]+\(|^def [^\n]+\("
        ),
        re.DOTALL,
    )
    SUPER_CLASS = re.compile(r"[A-Z_][_A-Za-z_0-9]+(?=[,\[\)])")
    methods = Methods()
