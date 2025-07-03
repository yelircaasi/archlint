import re
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from itertools import chain
from pathlib import Path
from typing import Self, cast

from .regexes import Regex
from .utils import (
    always_true,
    deduplicate_ordered,
    get_method_name,
    path_matches_not,
    project,
    remove_body,
    safe_search,
)

ClassInfo = tuple[Path, str, list[str], dict[str, str], list[str]]
ClassInfoPathless = tuple[str, list[str], dict[str, str], list[str]]


@dataclass
class Objects:
    functions: list[tuple[Path, str]]
    classes: list[ClassInfo]

    @property
    def function_strings(self) -> list[str]:
        return [f"{p}:{func}" for p, func in self.functions]

    @property
    def method_strings(self) -> list[str]:
        def _chain(_l: list[list]) -> list:
            return list(chain.from_iterable(_l))

        _classes = sorted(self.classes, key=lambda tup: tup[0])
        triples = _chain([[(p, c, m) for m in methods] for p, c, methods, _, __ in _classes])
        return [f"{p}:{c}.{m}" for p, c, m in triples]

    @property
    def strings(self) -> list[str]:
        return self.function_strings + self.method_strings

    @property
    def methodless(self) -> list[str]:
        return [f"{p}:{cl}" for p, cl, methods, _, __ in self.classes if not methods]

    def ignore_matching(self, pattern: re.Pattern) -> Self:
        self.functions = self.functions
        self.classes = self.classes
        return self

    def apply(
        self,
        processor: Callable[[str], str],
        ignore: re.Pattern | None = None,
        include_methodless: bool = False,
    ) -> list[str]:
        _strings: list[str] = self.strings + (self.methodless if include_methodless else [])
        if ignore:
            _strings = list(filter(partial(path_matches_not, path_pattern=ignore), _strings))
        return list(map(processor, _strings))


def collect_method_info(class_text: str) -> ClassInfoPathless:
    def is_method(_s: str) -> bool:
        return _s.startswith(("def", "@"))

    def fix_init(_s: str) -> str:
        _s = re.sub("\n    def __init__", "\n\n    def __init__", _s, count=1).strip()
        _s = re.sub('"""\n    def ', '"""\n\n    def ', _s, count=1)
        return re.sub(":\n    def ", ":\n\n    def ", _s, count=1)

    class_name = safe_search(Regex.CLASS_NAME, (class_text := fix_init(class_text)), 1)
    method_strings = list(filter(is_method, map(remove_body, class_text.split("\n\n    ")[1:])))
    method_names = deduplicate_ordered(map(get_method_name, method_strings))
    method_dict = {k: v for k, v in zip(method_names, method_strings) if k}
    super_classes = re.findall(Regex.SUPER_CLASS, class_text)
    method_names = list(filter(bool, method_names))

    return class_name, method_names, method_dict, super_classes


def collect_functions_in_text(
    src_text: str, condition: Callable[[str], bool] = always_true
) -> list[str]:
    return list(
        filter(
            condition,
            re.findall(Regex.FUNCTION_NAME, src_text) + re.findall(Regex.DATACLASS_NAME, src_text),
        )
    )


def collect_classes_in_text(src_text: str) -> list[ClassInfoPathless]:
    class_info: list[ClassInfoPathless] = []
    src_text = src_text.replace("@dataclass\nclass ", "\nclass ").replace("\n\n\n", "\n\n")
    classes = re.findall(Regex.CLASS_TEXT, src_text)
    for class_text in classes:
        class_name, method_names, method_dict, super_classes = collect_method_info(class_text)
        class_info.append((class_name, method_names, method_dict, super_classes))

    return class_info


def collect_tests_objects(unit_tests_dir: Path, project_root: Path) -> Objects:
    functions: list[tuple[Path, str]] = []
    classes: list[ClassInfo] = []

    for _p in sorted(unit_tests_dir.rglob("*.py")):
        source = _p.read_text()
        p = _p.relative_to(project_root)
        functions.extend(project(p, collect_functions_in_text(source)))
        classes.extend(project(p, collect_classes_in_text(source)))

    return Objects(functions=functions, classes=classes)


def collect_objects_in_md(
    src_text: str, condition: Callable[[str], bool] = always_true
) -> list[str]:
    # print(re.findall(Regex.OBJECT_IN_MD, src_text))
    return list(filter(condition, re.findall(Regex.OBJECT_IN_MD, src_text)))


def collect_docs_objects(md_dir: Path, project_root: Path) -> Objects:
    functions: list[tuple[Path, str]] = []

    for _p in sorted(md_dir.rglob("*.md")):
        # print(_p)
        source = _p.read_text()
        p = _p.relative_to(project_root)
        new_functions = cast(list[tuple[Path, str]], project(p, collect_objects_in_md(source)))
        functions.extend(new_functions)

    # print(functions)
    return Objects(functions=functions, classes=[])


def collect_source_objects(src_dir: Path) -> Objects:
    functions: list[tuple[Path, str]] = []
    classes: list[ClassInfo] = []

    for p in sorted(src_dir.rglob("*.py")):
        functions.extend(project(p, collect_functions_in_text(source := p.read_text())))
        classes.extend(project(p, collect_classes_in_text(source)))

    return Objects(functions=functions, classes=classes)


def add_inherited_methods(
    class_tuples: list[tuple[Path, str, list[str], list[str]]],
) -> list[tuple[Path, str, list[str], list[str]]]:
    methods = {name: methods for _, name, methods, __ in class_tuples}
    superclasses: dict[str, list[str]] = {name: supers for _, name, __, supers in class_tuples}

    for _ in range(2):
        for classname, superclass_names in superclasses.items():
            inherited = set(chain.from_iterable([methods.get(sc, []) for sc in superclass_names]))
            methods[classname] = list(set(methods[classname]) | inherited)

    return [(p, n, methods[n], s) for p, n, _, s in class_tuples]
