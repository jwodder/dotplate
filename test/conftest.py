from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
import shutil
import pytest

DATA_DIR = Path(__file__).with_name("data")


@pytest.fixture()
def tmp_home(
    monkeypatch: pytest.MonkeyPatch, tmp_path_factory: pytest.TempPathFactory
) -> Path:
    """
    A fixture that sets :envvar:`HOME` to a temporary path and returns that
    path
    """
    home = tmp_path_factory.mktemp("tmp_home")
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    monkeypatch.delenv("XDG_CONFIG_DIRS", raising=False)
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.delenv("XDG_DATA_DIRS", raising=False)
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    monkeypatch.delenv("XDG_RUNTIME_DIR", raising=False)
    monkeypatch.delenv("XDG_STATE_HOME", raising=False)
    monkeypatch.setenv("USERPROFILE", str(home))
    monkeypatch.setenv("LOCALAPPDATA", str(home))
    return home


@dataclass
class CaseDirs:
    src: Path  # temporary directory
    dest: Path  # directory in this repository


def case_fixture(name: str) -> Callable[..., CaseDirs]:
    @pytest.fixture(name=name.replace("-", "_"))
    def fixture(tmp_path_factory: pytest.TempPathFactory) -> CaseDirs:
        casedir = DATA_DIR / "cases" / name
        src = tmp_path_factory.mktemp(f"{name}_src")
        shutil.copytree(casedir / "src", src, dirs_exist_ok=True)
        return CaseDirs(src=src, dest=casedir / "dest")

    return fixture


custom_brackets = case_fixture("custom-brackets")
next_to_src = case_fixture("next-to-src")
script = case_fixture("script")
simple = case_fixture("simple")
