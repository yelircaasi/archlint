import re

from click.testing import CliRunner

from archlint.cli import (
    main,
    archlint_cli,
    run_all,
    docs,
    imports,
    methods,
    tsts,
)


def test_main(capsys):
    main()
    text = capsys.readouterr().out
    assert len(re.findall("Hello", text)) == 4
    assert len(re.findall(r"[a-z-_]+ version: \d+\.\d+", text)) == 3


def test_archlint_cli(capsys):
    runner = CliRunner()
    result = runner.invoke(archlint_cli)
    assert result.exit_code == 0
    assert "No problems detected." in result.output


def test_run_all(capsys):
    runner = CliRunner()
    result = runner.invoke(archlint_cli, ["all"])
    assert result.exit_code == 0
    assert "No problems detected." in result.output


def test_docs(capsys):
    runner = CliRunner()
    result = runner.invoke(archlint_cli, ["docs"])
    assert result.exit_code == 0
    assert "No problems detected." in result.output


def test_imports(capsys):
    runner = CliRunner()
    result = runner.invoke(archlint_cli, ["imports"])
    assert result.exit_code == 0
    assert "No problems detected." in result.output


def test_methods(capsys):
    runner = CliRunner()
    result = runner.invoke(archlint_cli, ["methods"])
    assert result.exit_code == 0
    assert "No problems detected." in result.output


def test_tests(capsys):
    runner = CliRunner()
    result = runner.invoke(archlint_cli, ["tests"])
    assert result.exit_code == 0
    assert "No problems detected." in result.output
