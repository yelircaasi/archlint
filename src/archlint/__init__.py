from functools import partial

from archlint.logic import sort_methods
from archlint.utils import deduplicate_ordered, make_double_bar, sort_on_path

from .collection import Objects
from .configuration import Configuration
from .logic import (
    analyze_discrepancies,
    get_disallowed_imports,
    map_to_doc,
    map_to_test,
)
from .reporting import (
    make_discrepancy_report,
    make_imports_report,
    make_methods_report,
)


def check_method_order(cfg: Configuration, source_objects: Objects) -> tuple[str, bool]:
    make_double_bar(" METHOD ORDER ")

    out_of_order = []
    classes = source_objects.classes

    for path, classname, methods, method_dict, _ in classes:
        sorted_methods = sort_methods(method_dict, cfg.method_order)
        if methods != sorted_methods:
            out_of_order.append((path, classname, methods, sorted_methods))

    return make_methods_report(out_of_order), bool(out_of_order)


def check_docs_structure(
    cfg: Configuration, source_objects: Objects, docs_objects: Objects
) -> tuple[str, bool]:
    actual: list[str] = sort_on_path(docs_objects.strings)
    duplicated = source_objects.apply(
        partial(map_to_doc, cfg=cfg), cfg.docs.ignore, include_methodless=True
    )
    expected: list[str] = sort_on_path(deduplicate_ordered(duplicated))
    missing, unexpected = analyze_discrepancies(
        actual, expected, allow_additional=cfg.docs.allow_additional
    )

    # print(actual)
    # print()
    # print(docs_objects.strings)

    return (
        make_discrepancy_report(
            "DOCUMENTATION", missing, unexpected, cfg.docs.md_dir, cfg.root_dir
        ),
        any((missing, unexpected)),
    )


def check_tests_structure(
    cfg: Configuration, source_objects: Objects, tests_objects: Objects
) -> tuple[str, bool]:
    actual: list[str] = sort_on_path(tests_objects.strings)
    expected: list[str] = sort_on_path(
        source_objects.apply(partial(map_to_test, cfg=cfg), cfg.tests.ignore)
    )
    missing, unexpected = analyze_discrepancies(
        actual, expected, allow_additional=cfg.tests.allow_additional
    )

    return (
        make_discrepancy_report("TESTS", missing, unexpected, cfg.tests.unit_dir, cfg.root_dir),
        any((missing, unexpected)),
    )


def check_imports(cfg: Configuration) -> tuple[str, bool]:
    internal, external = get_disallowed_imports(cfg.imports, cfg.module_name)

    return (
        make_imports_report(internal, external),
        any((internal, external)),
    )
