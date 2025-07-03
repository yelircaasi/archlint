import os
from pathlib import Path

import pytest

TEST_ROOT = Path(__file__).parent
PROJECT_ROOT = TEST_ROOT.parent


class Helpers:
    @staticmethod
    def help_me():
        return "no"


@pytest.fixture
def helpers():
    return Helpers


@pytest.fixture
def project_root():
    return PROJECT_ROOT


@pytest.fixture
def tst_root():
    return TEST_ROOT


def patch_env(mocker, name: str, value: str) -> None:
    mocker.patch("os.environ", os.environ | {name: value})
