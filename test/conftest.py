from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass
import json
from pathlib import Path
import shutil
import pytest
from pytest_mock import MockerFixture

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


@pytest.fixture
def casedirs(
    mocker: MockerFixture,
    request: pytest.FixtureRequest,
    tmp_path_factory: pytest.TempPathFactory,
) -> CaseDirs:
    if (name := getattr(request, "param", None)) is None:
        if (mark := request.node.get_closest_marker("usecase")) is not None:
            try:
                (name,) = mark.args
            except ValueError:
                raise pytest.UsageError("usecase takes exactly one argument")
        else:
            raise pytest.UsageError(
                "casedir fixture must be accompanied by usecase mark"
            )
    casedir = DATA_DIR / "cases" / name
    src = tmp_path_factory.mktemp(f"{name}_src")
    shutil.copytree(casedir / "src", src, dirs_exist_ok=True)
    if (specfile := (casedir / "which-mock.json")).exists():
        spec = json.loads(specfile.read_text(encoding="utf-8"))
        mocker.patch("shutil.which", side_effect=make_which_mock(spec))
    return CaseDirs(src=src, dest=casedir / "dest")


def make_which_mock(spec: dict[str, str | None]) -> Callable[[str], str | None]:
    def which_mock(cmd: str) -> str | None:
        return spec[cmd]

    return which_mock
