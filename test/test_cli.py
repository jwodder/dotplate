from __future__ import annotations
from operator import attrgetter
from pathlib import Path
from traceback import format_exception
from click.testing import CliRunner, Result
from conftest import CaseDirs
import pytest
from dotplate.__main__ import main
from dotplate.util import is_executable

DATA_DIR = Path(__file__).with_name("data")


def show_result(r: Result) -> str:
    if r.exception is not None:
        assert isinstance(r.exc_info, tuple)
        return "".join(format_exception(*r.exc_info))
    else:
        return r.output


def assert_dirtrees_eq(tree1: Path, tree2: Path) -> None:
    """
    Assert that the directory hierarchies at ``tree1`` and ``tree2`` have the
    same files with the same contents.

    For use in writing pytest tests.
    """
    assert sorted(map(attrgetter("name"), tree1.iterdir())) == sorted(
        map(attrgetter("name"), tree2.iterdir())
    )
    for p1 in tree1.iterdir():
        p2 = tree2 / p1.name
        assert p1.is_dir() == p2.is_dir()
        if p1.is_dir():
            assert_dirtrees_eq(p1, p2)
        else:
            assert p1.read_text(encoding="utf-8") == p2.read_text(encoding="utf-8")
            assert is_executable(p1) == is_executable(p2)


@pytest.mark.parametrize(
    "casedirs", sorted(p.name for p in (DATA_DIR / "cases").iterdir()), indirect=True
)
def test_install(
    monkeypatch: pytest.MonkeyPatch, tmp_home: Path, casedirs: CaseDirs
) -> None:
    monkeypatch.chdir(casedirs.src)
    r = CliRunner().invoke(main, ["install", "--yes"], standalone_mode=False)
    assert r.exit_code == 0, show_result(r)
    assert_dirtrees_eq(tmp_home, casedirs.dest)


@pytest.mark.usecase("suited")
def test_install_suite_enabled(
    monkeypatch: pytest.MonkeyPatch, tmp_home: Path, casedirs: CaseDirs
) -> None:
    monkeypatch.chdir(casedirs.src)
    r = CliRunner().invoke(
        main, ["--enable-suite=vim", "install", "--yes"], standalone_mode=False
    )
    assert r.exit_code == 0, show_result(r)
    assert_dirtrees_eq(tmp_home, casedirs.dest.with_name("dest-vim"))


@pytest.mark.usecase("suite-enabled")
def test_install_suite_disabled(
    monkeypatch: pytest.MonkeyPatch, tmp_home: Path, casedirs: CaseDirs
) -> None:
    monkeypatch.chdir(casedirs.src)
    r = CliRunner().invoke(
        main, ["--disable-suite=vim", "install", "--yes"], standalone_mode=False
    )
    assert r.exit_code == 0, show_result(r)
    assert_dirtrees_eq(tmp_home, casedirs.dest.with_name("dest-no-vim"))


@pytest.mark.parametrize(
    "args,destdir",
    [
        (["--enable-suite=bar"], "dest-foobar"),
        (["--enable-suite=bar", "--disable-suite=foo"], "dest-bar"),
        (["--disable-suite=foo"], "dest-neither"),
    ],
)
@pytest.mark.usecase("multisuite")
def test_install_multisuite(
    monkeypatch: pytest.MonkeyPatch,
    tmp_home: Path,
    casedirs: CaseDirs,
    args: list[str],
    destdir: str,
) -> None:
    monkeypatch.chdir(casedirs.src)
    r = CliRunner().invoke(main, [*args, "install", "--yes"], standalone_mode=False)
    assert r.exit_code == 0, show_result(r)
    assert_dirtrees_eq(tmp_home, casedirs.dest.with_name(destdir))
