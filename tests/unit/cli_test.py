import re

from click.testing import CliRunner

from archlint.cli import (
    archlint_cli,
    main,
)


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


def test_tsts(capsys):
    runner = CliRunner()
    result = runner.invoke(archlint_cli, ["tests"])
    assert result.exit_code == 0
    assert "No problems detected." in result.output
