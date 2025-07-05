import re

from archlint.cli import main


def test_archlint_cli():
    # TODO
    ...


def test_tests():
    # TODO
    ...


def test_docs():
    # TODO
    ...


def test_imports():
    # TODO
    ...


def test_methods():
    # TODO
    ...


def test_main(capsys):
    main()
    text = capsys.readouterr().out
    assert len(re.findall("Hello", text)) == 4
    assert len(re.findall(r"[a-z-_]+ version: \d+\.\d+", text)) == 3
