from collections.abc import Callable
from pathlib import Path

import pytest

from archlint.reporting import (
    display_disallowed,
    make_discrepancy_report,
    make_imports_report,
    make_methods_report,
    make_missing_report,
    make_order_report,
    make_unexpected_report,
)
from archlint.utils import Color


def test_make_methods_report():
    result = make_methods_report([])
    assert "METHOD ORDER" in result
    assert "No problems detected." in result

    report = make_methods_report([(Path("some/file.py"), "MyClass", ["a", "b"], ["a", "c"])])
    assert "MyClass" in report
    assert "some/file.py" in report
    assert "a" in report
    assert "c" in report


@pytest.mark.parametrize(
    "violations, contained, noncontained",
    [
        ({}, ["No problems detected."], []),
        ({"mod1": {"foo", "bar"}, "mod2": set()}, ["mod1", "bar", "foo"], ["mod2"]),
    ],
    ids=["empty", "nonempty"],
)
def test_display_disallowed(violations: dict, contained: list[str], noncontained: list[str]):
    result = display_disallowed(violations)
    for substring in contained:
        assert substring in result
    for substring in noncontained:
        assert substring not in result


@pytest.mark.parametrize(
    "internal_violations, external_violations, painter, contained, noncontained",
    [
        ({}, {}, Color.green, ["No problems detected."], ["missing"]),
        (
            {"a": {"module_a"}},
            {"b": {"bar"}},
            Color.red,
            ["module_a", "bar", "EXTERNAL IMPORTS", "INTERNAL MODULE IMPORTS"],
            ["o problems "],
        ),
    ],
    ids=["empty", "nonempty"],
)
def test_make_imports_report(
    internal_violations: dict[str, set[str]],
    external_violations: dict[str, set[str]],
    painter: Callable[[str], str],
    contained: list[str],
    noncontained: list[str],
):
    result = make_imports_report(internal_violations, external_violations)
    for substring in contained:
        assert substring in result
    for substring in noncontained:
        assert substring not in result


def test_make_missing_report():
    assert make_missing_report([], lambda s: s) == ""

    result = make_missing_report(["a", "b"], lambda s: f"{s}")
    assert "MISSING" in result
    assert "a" in result
    assert "b" in result


def test_make_unexpected_report():
    assert make_unexpected_report([], lambda s: s) == ""

    result = make_unexpected_report(["a", "b"], lambda s: f"{s}")
    assert "UNEXPECTED" in result
    assert "a" in result
    assert "b" in result


def test_make_order_report():
    result = make_order_report([], [], set(), lambda s: s)
    assert result == ""

    actual = ["mod:a", "mod:b"]
    expected = ["mod:a", "mod:b"]
    overlap = {"mod:a", "mod:b"}
    result = make_order_report(actual, expected, overlap, lambda s: s)
    assert result == ""

    actual = ["mod:a", "mod:b"]
    expected = ["mod:b", "mod:a"]
    overlap = {"mod:a", "mod:b"}
    result = make_order_report(actual, expected, overlap, lambda s: f"{s}")
    assert "ORDERING MISMATCH" in result
    assert "mod:a" in result
    assert "a" in result or "b" in result

    actual = ["mod:a", "mod:c", "mod:b"]
    expected = ["mod:a", "mod:b", "mod:c"]
    overlap = {"mod:a", "mod:b", "mod:c"}
    result = make_order_report(actual, expected, overlap, lambda s: s)
    assert "mod:b" in result
    assert "mod:c" in result


def test_make_discrepancy_report(tmp_path):
    report = make_discrepancy_report(
        "test", ["a"], ["a"], [], [], {"a"}, specific_path=tmp_path / "x.py", root_dir=tmp_path
    )
    assert "No problems detected" in report
    assert "TEST" in report

    report = make_discrepancy_report(
        "demo",
        ["1", "2"],
        ["2", "3"],
        ["3"],
        ["1"],
        {"2"},
        specific_path=tmp_path / "demo.py",
        root_dir=tmp_path,
    )
    assert "MISSING" in report
    assert "3" in report
    assert "UNEXPECTED" in report
    assert "1" in report
