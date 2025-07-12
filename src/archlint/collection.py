"""
Class and functions tasked with finding and processing code objects in the source files.
"""

import re
from collections.abc import Callable
from functools import partial
from itertools import chain
from pathlib import Path

from .regexes import Regex
from .utils import (
    always_true,
    deduplicate_ordered,
    get_method_name,
    path_matches_not,
    remove_body,
    safe_search,
)

ClassInfo = tuple[Path, int, str, list[str], dict[str, str], list[str]]
ClassInfoBase = tuple[str, list[str], dict[str, str], list[str]]


class Objects:
    """
    Dataclass to hold information collected on objects.

    Used with source, test, and documentation objects, but only one of these per instance.
    """

    def __init__(self, functions: list[tuple[Path, int, str]], classes: list[ClassInfo]):
        self.functions = functions
        self.classes = add_inherited_methods(classes)

    @property
    def function_strings(self) -> list[str]:
        return [f"{p}:{i:0>3}:{func}" for p, i, func in self.functions]

    @property
    def method_strings(self) -> list[str]:
        def _chain(_l: list[list]) -> list:
            return list(chain.from_iterable(_l))

        _classes = sorted(self.classes, key=lambda tup: tup[0])
        quads = _chain([[(p, i, c, m) for m in methods] for p, i, c, methods, _, __ in _classes])
        return [f"{p}:{i:0>3}:{c}.{m}" for p, i, c, m in quads]

    @property
    def strings(self) -> list[str]:
        return self.method_strings + self.function_strings

    @property
    def strings_without_methods(self) -> list[str]:
        return self.classes_only + self.function_strings

    @property
    def classes_only(self) -> list[str]:
        return list(set([f"{p}:{i:0>3}:{cl}" for p, i, cl, _, __, ___ in self.classes]))

    @property
    def methodless(self) -> list[str]:
        return [f"{p}:{i:0>3}:{cl}" for p, i, cl, methods, _, __ in self.classes if not methods]

    def apply(
        self,
        processor: Callable[[str], str],
        ignore: re.Pattern | None = None,
        classes_only: bool = False,
    ) -> list[str]:
        _strings: list[str]
        if classes_only:
            _strings = self.classes_only + self.function_strings
        else:
            _strings = self.strings
        if ignore:
            _strings = list(filter(partial(path_matches_not, path_pattern=ignore), _strings))
        return list(filter(bool, map(processor, _strings)))


def collect_method_info(class_text: str) -> ClassInfoBase:
    def is_method(_s: str) -> bool:
        return _s.startswith(("def", "@"))

    def fix_init(_s: str) -> str:
        _s = _s.replace(":\n", ":\n\n")
        _s = re.sub("\n    def __init__", "\n\n    def __init__", _s, count=1).strip()
        _s = re.sub('"""\n    def ', '"""\n\n    def ', _s, count=1)
        return re.sub(":\n    def ", ":\n\n    def ", _s, count=1)

    class_name = safe_search(Regex.CLASS_NAME, (class_text := fix_init(class_text)), 1)
    method_strings = list(filter(is_method, map(remove_body, class_text.split("\n\n    ")[1:])))
    method_names = deduplicate_ordered(map(get_method_name, method_strings))
    method_dict = {k: v for k, v in zip(method_names, method_strings) if k}
    super_classes = re.findall(Regex.SUPER_CLASS, class_text.split(":\n")[0])
    method_names = list(filter(bool, method_names))

    return class_name, method_names, method_dict, super_classes


def parse_function(src_text: str, condition: Callable[[str], bool] = always_true) -> str:
    return safe_search(Regex.FUNCTION_NAME, src_text, 1)


def collect_objects_in_md(
    src_text: str, condition: Callable[[str], bool] = always_true
) -> list[tuple[int, str]]:
    return list(enumerate(filter(condition, re.findall(Regex.OBJECT_IN_MD, src_text))))


def collect_docs_objects(md_dir: Path, project_root: Path) -> Objects:
    functions: list[tuple[Path, int, str]] = []
    code_block = re.compile(r"```.+?```", re.DOTALL)

    for _p in sorted(md_dir.rglob("*.md")):
        p = _p.relative_to(project_root) if _p.is_absolute() else _p
        source = str(p.read_text())  # hack for testing purposes, to make mock work
        source = re.sub(code_block, "", source)

        for new_objects in collect_objects_in_md(source):
            functions.append((p, *new_objects))

    return Objects(functions=functions, classes=[])


def collect_object_texts(source: str) -> list[str]:
    source = str(source)  # hack for testing purposes, to make mock work
    multiline_comment = re.compile(r"\"\"\".+?\"\"\"", re.DOTALL)
    code_block = re.compile(r"```.+?```", re.DOTALL)
    comment = re.compile(r"\n#[^\n]+\n", re.DOTALL)
    source = re.sub(multiline_comment, '"""  """', source)
    source = re.sub(code_block, "```\n\n```", source)
    source = re.sub(comment, "```\n\n```", source)
    return re.findall(Regex.OBJECT_TEXT, source)


def collect_source_objects(src_dir: Path, root_dir: Path) -> Objects:
    functions: list[tuple[Path, int, str]] = []
    classes: list[ClassInfo] = []

    for _p in sorted(src_dir.rglob("*.py")):
        p = _p.relative_to(root_dir) if _p.is_absolute() else _p
        for i, text in enumerate(collect_object_texts(_p.read_text())):
            if text.startswith(("@dataclass", "class ")) and (
                class_tuple := collect_method_info(text)
            ):
                classes.append((p, i, *class_tuple))
            elif text.startswith(("@", "def ")) and (func_name := parse_function(text)):
                functions.append((p, i, func_name))

    return Objects(functions=functions, classes=classes)


def add_inherited_methods(class_tuples: list[ClassInfo]) -> list[ClassInfo]:
    methods = {d[2]: d[3] for d in class_tuples}
    superclasses = {d[2]: d[5] for d in class_tuples}

    for _ in range(2):
        for classname, superclass_names in superclasses.items():
            inherited = list(chain.from_iterable([methods.get(sc, []) for sc in superclass_names]))
            methods[classname] = deduplicate_ordered(methods[classname] + inherited)

    return [(p, i, n, methods[n], md, s) for p, i, n, _, md, s in class_tuples]
