from pathlib import Path

import pytest

from student_success import config


def test_optional_path_returns_none_when_missing(monkeypatch):
    monkeypatch.delenv("TEST_OPTIONAL_PATH", raising=False)

    assert config._get_optional_path("TEST_OPTIONAL_PATH") is None


def test_optional_path_returns_path(monkeypatch):
    monkeypatch.setenv("TEST_OPTIONAL_PATH", r"C:\test\data")

    result = config._get_optional_path("TEST_OPTIONAL_PATH")

    assert isinstance(result, Path)
    assert str(result) == r"C:\test\data"


def test_required_setting_returns_value(monkeypatch):
    monkeypatch.setenv("TEST_REQUIRED_SETTING", "test_value")

    assert config._get_required("TEST_REQUIRED_SETTING") == "test_value"


def test_required_setting_missing_raises(monkeypatch):
    monkeypatch.delenv("TEST_REQUIRED_SETTING", raising=False)

    with pytest.raises(RuntimeError):
        config._get_required("TEST_REQUIRED_SETTING")