"""
Functions implementing the core of the code analysis logic.
"""

import re
from pathlib import Path

import grimp

from .configuration import Configuration, ImportsConfig, MethodsConfig
from .regexes import Regex
from .utils import (
    dedup_underscores,
    filter_with,
    filter_without,
    move_path,
    path_matches,
    remove_ordering_index,
)

SetDict = dict[str, set[str]]


def make_test_method(s: str) -> str:
    if re.search(Regex.DUNDER, s):
        return f"test_dunder_{s[2:-2]}"
    return f"test_{s}"


def fix_dunder_filename(p: Path) -> Path:
    if p.name == "__init__.py":
        return p.parent / "init.py"
    if p.name == "__main__.py":
        return p.parent / "main.py"
    return p


def make_test_filename(p: Path, use_filename_suffix: bool = True) -> Path:
    p = fix_dunder_filename(p)
    if use_filename_suffix:
        return p.parent / f"{p.name.replace('.py', '')}_test.py"
    return p.parent / f"test_{p.name}"


def make_doc_filename(p: Path) -> Path:
    p = fix_dunder_filename(p)
    return p.parent / f"{p.name.replace('.py', '')}.md"


def make_test_method_path(
    p: Path,
    i: str,
    class_name: str,
    method_name: str,
    file_per_class: re.Pattern,
    file_per_directory: re.Pattern,
) -> str:
    if path_matches(p, file_per_class):
        p = p.parent / p.name.replace(".py", "") / class_name.lower()
    else:
        p = path_matches(p, file_per_directory) or p

    return f"{make_test_filename(p)}:{i:0>3}:Test{class_name}.{make_test_method(method_name)}"


def make_doc_class_path(
    p: Path,
    i: str,
    class_name: str,
    file_per_class: re.Pattern,
    file_per_directory: re.Pattern,
) -> str:
    if path_matches(p, file_per_class):
        p = p.parent / p.name.replace(".py", "") / class_name.lower()
    else:
        p = path_matches(p, file_per_directory) or p

    return f"{make_doc_filename(p)}:{i:0>3}:{class_name}"


def make_test_function_path(
    p: Path, i: str, function_name: str, file_per_directory: re.Pattern
) -> str:
    p = path_matches(p, file_per_directory) or p
    return f"{make_test_filename(p)}:{i:0>3}:test_{function_name}"


def make_doc_function_path(
    p: Path, i: str, function_name: str, file_per_directory: re.Pattern
) -> str:
    p = path_matches(p, file_per_directory) or p
    return f"{make_doc_filename(p)}:{i:0>3}:{function_name}"


def map_to_test(s: str, cfg: Configuration) -> str:
    path_str, i, ob = s.split(":")
    path_ = move_path(path_str, cfg.module_root_dir, cfg.tests.unit_dir)
    if path_.is_absolute():
        path_ = path_.relative_to(cfg.root_dir)
    if "." in ob:
        class_name, method_name = ob.split(".")
        result = make_test_method_path(
            path_,
            i,
            class_name,
            method_name,
            cfg.tests.file_per_class,
            cfg.tests.file_per_directory,
        )
    elif ob[0].isupper():
        return ""
    else:
        result = make_test_function_path(path_, i, ob, cfg.tests.file_per_directory)
    return dedup_underscores(result) if cfg.tests.replace_double_underscore else result


def map_to_doc(s: str, cfg: Configuration) -> str:
    path_str, i, ob = s.split(":")
    path_ = move_path(path_str, cfg.module_root_dir, cfg.docs.md_dir)
    if path_.is_absolute():
        path_ = path_.relative_to(cfg.root_dir)
    if "." in ob:
        class_name, _ = ob.split(".")
        result = make_doc_class_path(
            path_, i, class_name, cfg.docs.file_per_class, cfg.docs.file_per_directory
        )
    else:
        result = make_doc_function_path(path_, i, ob, cfg.docs.file_per_directory)
    return dedup_underscores(result) if cfg.docs.replace_double_underscore else result


def compute_disallowed(
    allowed: SetDict,
    disallowed: SetDict,
    allowed_everywhere: set[str],
    graph: grimp.ImportGraph,
) -> SetDict:
    violations: SetDict = {s: set() for s in set(allowed) | set(disallowed)}
    if allowed and disallowed:
        print(
            "Specifying 'allowed' and 'disallowed' imports does not make sense; "
            "using 'allowed' (restrictive)."
        )
    if allowed:
        for module, imports in allowed.items():
            if module not in graph.modules:
                print(f"    '{module}' is not a module or is not on the import tree.")
                continue
            upstream = graph.find_upstream_modules(module)
            own_submodules = {module} | filter_with(upstream, module)
            via_allowed = filter_without(
                upstream,
                imports | own_submodules | allowed_everywhere,
            )
            violations[module].update(via_allowed)
    else:
        for module, imports in disallowed.items():
            if module not in graph.modules:
                print(f"    '{module}' is not a module or is not on the import tree.")
                continue
            upstream = graph.find_upstream_modules(module)
            via_disallowed = filter_with(upstream, imports)
            violations[module].update(via_disallowed)

    return {m: ss for m, ss in violations.items() if ss}


def get_disallowed_imports(icfg: ImportsConfig, module_name: str) -> tuple[SetDict, SetDict]:
    internal_graph = grimp.build_graph(
        module_name,
        include_external_packages=False,
        cache_dir=icfg.grimp_cache,
    )
    external_graph = grimp.build_graph(
        module_name,
        include_external_packages=True,
        cache_dir=icfg.grimp_cache,
    )
    internal_disallowed = compute_disallowed(
        icfg.internal.allowed,
        icfg.internal.disallowed,
        icfg.internal_allowed_everywhere,
        internal_graph,
    )
    external_disallowed = compute_disallowed(
        icfg.external.allowed,
        icfg.external.disallowed,
        icfg.external_allowed_everywhere,
        external_graph,
    )

    return internal_disallowed, external_disallowed


def sort_methods(method_dict: dict[str, str], cfg: MethodsConfig) -> list[str]:
    regex_pairs: tuple[tuple[re.Pattern, float], ...] = cfg.ordering
    normal_value: float = cfg.normal

    def classify_method(s: str) -> float:
        for regexp, value in regex_pairs:
            if re.search(regexp, s):
                return value
        return normal_value

    return sorted(method_dict, key=lambda k: classify_method(method_dict[k]))


def analyze_discrepancies(
    expected: list[str],
    actual: list[str],
    allow_additional: re.Pattern,
) -> tuple[list[str], list[str], set[str]]:
    actual_set = set(actual := list(map(remove_ordering_index, actual)))
    expected_set = set(expected := list(map(remove_ordering_index, expected)))

    missing: list[str] = [t for t in expected if t not in actual_set]
    unexpected: list[str] = [
        t for t in actual if (t not in expected_set) and not re.search(allow_additional, t)
    ]
    overlap = actual_set.intersection(expected_set)

    return missing, unexpected, overlap
