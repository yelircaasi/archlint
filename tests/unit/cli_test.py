import re

from archlint.cli import main


def test_archlint_cli(): ...


def test_tests(): ...


def test_docs(): ...


def test_imports(): ...


def test_methods(): ...


def test_main(capsys):
    main()
    text = capsys.readouterr().out
    assert len(re.findall("Hello", text)) == 4
    assert len(re.findall(r"[a-z-_]+ version: \d+\.\d+", text)) == 3
