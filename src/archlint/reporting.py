import re
from pathlib import Path

from .utils import (
    Color,
    make_bar,
    make_colorize_path,
    make_double_bar,
)


def make_methods_report(info: list[tuple[Path, str, list[str], list[str]]]) -> str:
    def make_class_report(info_tuple: tuple[Path, str, list[str], list[str]]) -> str:
        p, class_name, methods, sorted_methods = info_tuple
        return (
            f"\n{make_bar(' ' + class_name + ' ', colorizer=Color.red)}\n{p}\n\n"
            f"{'\n'.join(map(make_line, zip(methods, sorted_methods)))}"
        )

    def make_line(method_pair: tuple[str, str]) -> str:
        actual_method, expected_method = method_pair
        if actual_method == expected_method:
            return f"    {actual_method}"
        else:
            return f"    {actual_method + '  ':─<30}  {Color.red(expected_method)}"

    if not info:
        return (
            "\n"
            + make_double_bar(" METHOD ORDER ")
            + "\n\n"
            + Color.green("    No problems detected.")
        )
    return (
        "\n" + make_double_bar(" METHOD ORDER ") + "\n" + "\n\n".join(map(make_class_report, info))
    )


def display_disallowed(disallowed: dict[str, set[str]]) -> str:
    def make_line(mod_probs: tuple[str, set[str]]) -> str:
        mod, probs = mod_probs
        return (
            f"    {Color.cyan(mod)}\n\n    "
            f"\n        {'\n        '.join(map(Color.red, sorted(probs)))}{'\n' * bool(probs)}"
        )

    if disallowed and any(disallowed.values()):
        items = list(filter(lambda tup: bool(tup[1]), disallowed.items()))
        return re.sub(
            r"\n+ *\n+",
            "\n\n",
            "\n\n".join(map(make_line, items)),
        )
    return Color.green("    No problems detected.")


def make_imports_report(
    disallowed_internal: dict[str, set[str]], disallowed_external: dict[str, set[str]]
) -> str:
    return (
        f"\n{make_double_bar(' INTERNAL MODULE IMPORTS ')}\n\n"
        f"{display_disallowed(disallowed_internal)}\n\n"
        f"{make_double_bar(' EXTERNAL IMPORTS ')}\n\n"
        f"{display_disallowed(disallowed_external)}"
    )


def make_discrepancy_report(
    title: str,
    missing: list[str],
    unexpected: list[str],
    specific_path: Path,
    root_dir: Path,
):
    paint = make_colorize_path(specific_path, root_dir)
    title = f" {title.upper()} "
    if not (missing or unexpected):
        return f"\n{make_double_bar(title)}\n\n    {Color.green('No problems detected.')}"
    return (
        f"\n{make_double_bar(title)}\n\n"
        f"{make_bar(' MISSING ', Color.red)}\n\n"
        f"    {'\n    '.join(map(paint, missing))}\n\n"
        f"{make_bar(' UNEXPECTED ', Color.red)}\n\n"
        f"    {'\n    '.join(map(paint, unexpected))}"
    ).replace("\n\n\n", "\n\n")
