import re
from pathlib import Path

import grimp

from .configuration import Configuration, ImportConfig, MethodOrderConfig
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
    if _p := path_matches(p, file_per_class):
        p = _p.parent / class_name.lower()
    else:
        p = path_matches(p, file_per_directory) or p

    return f"{make_test_filename(p)}:{i}:Test{class_name}.{make_test_method(method_name)}"


def make_doc_class_path(p: Path, i: str, class_name: str, cfg: Configuration) -> str:
    if _p := path_matches(p, cfg.docs.file_per_class):
        p = _p.parent / class_name.lower()
    else:
        p = path_matches(p, cfg.docs.file_per_directory) or p

    return f"{make_doc_filename(p)}:{i}:{class_name}"


def make_test_function_path(p: Path, i: str, function_name: str, cfg: Configuration) -> str:
    p = path_matches(p, cfg.tests.file_per_directory) or p
    return f"{make_test_filename(p)}:{i}:test_{function_name}"


def make_doc_function_path(p: Path, i: str, function_name: str, cfg: Configuration) -> str:
    p = path_matches(p, cfg.docs.file_per_directory) or p
    return f"{make_doc_filename(p)}:{i}:{function_name}"


def map_to_test(s: str, cfg: Configuration) -> str:
    path_str, i, ob = s.split(":")
    path_ = move_path(path_str, cfg.module_root_dir, cfg.tests.unit_dir, cfg.root_dir)
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
        result = make_test_function_path(path_, i, ob, cfg)
    if not cfg.tests.keep_double_underscore:
        return dedup_underscores(result)
    return result


def map_to_doc(s: str, cfg: Configuration) -> str:
    path_str, i, ob = s.split(":")
    path_ = move_path(path_str, cfg.module_root_dir, cfg.docs.md_dir, cfg.root_dir)
    if "." in ob:
        class_name, _ = ob.split(".")
        result = make_doc_class_path(path_, i, class_name, cfg)
    else:
        result = make_doc_function_path(path_, i, ob, cfg)
    if not cfg.docs.keep_double_underscore:
        return dedup_underscores(result)
    return result


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

    return violations


def get_disallowed_imports(icfg: ImportConfig, module_name: str) -> tuple[SetDict, SetDict]:
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
        icfg.allowed.internal,
        icfg.disallowed.internal,
        icfg.internal_allowed_everywhere,
        internal_graph,
    )
    external_disallowed = compute_disallowed(
        icfg.allowed.external,
        icfg.disallowed.external,
        icfg.external_allowed_everywhere,
        external_graph,
    )

    return internal_disallowed, external_disallowed


def sort_methods(method_dict: dict[str, str], cfg: MethodOrderConfig) -> list[str]:
    regex_pairs: tuple[tuple[re.Pattern, float], ...] = cfg.ordering
    normal_value: float = cfg.normal

    def classify_method(s: str) -> float:
        for regexp, value in regex_pairs:
            if re.search(regexp, s):
                return value
        return normal_value

    return sorted(method_dict, key=lambda k: classify_method(method_dict[k]))


def analyze_discrepancies(
    actual: list[str],
    expected: list[str],
    allow_additional: bool = False,
) -> tuple[list[str], list[str], set[str]]:
    actual_set = set(actual := list(map(remove_ordering_index, actual)))
    expected_set = set(expected := list(map(remove_ordering_index, expected)))

    missing = [t for t in expected if t not in actual_set]
    unexpected = [] if allow_additional else [t for t in actual if t not in expected_set]
    overlap = actual_set.intersection(expected_set)

    return missing, unexpected, overlap
