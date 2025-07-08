import re
import subprocess

from archlint.cli import (
    main,
)


def test_main(capsys):
    main()
    text = capsys.readouterr().out
    assert len(re.findall("Hello", text)) == 4
    assert len(re.findall(r"[a-z-_]+ version: \d+\.\d+", text)) == 3


def test_archlint_cli(capsys):
    result = subprocess.run(["archlint"], capture_output=True, check=False).stdout
    assert "No problems detected." in result


def test_run_all(capsys):
    result = subprocess.run(["archlint", "all"], capture_output=True, check=False).stdout
    assert "No problems detected." in result


def test_docs(capsys):
    result = subprocess.run(["archlint", "docs"], capture_output=True, check=False).stdout
    assert "No problems detected." in result


def test_imports(capsys):
    result = subprocess.run(["archlint", "imports"], capture_output=True, check=False).stdout
    assert "No problems detected." in result


def test_methods(capsys):
    result = subprocess.run(["archlint", "methods"], capture_output=True, check=False).stdout
    assert "No problems detected." in result


def test_tests(capsys):
    result = subprocess.run(["archlint", "tests"], capture_output=True, check=False).stdout
    assert "No problems detected." in result
