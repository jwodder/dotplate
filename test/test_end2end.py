from __future__ import annotations
from operator import attrgetter
from pathlib import Path
from shutil import copytree
from traceback import format_exception
from click.testing import CliRunner, Result
import pytest
from dotplate.__main__ import main

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


@pytest.mark.parametrize("casedir", sorted((DATA_DIR / "examples").iterdir()))
def test_end2end(
    monkeypatch: pytest.MonkeyPatch, tmp_home: Path, tmp_path: Path, casedir: Path
) -> None:
    tmp_path /= "tmp"  # copytree() can't copy to a dir that already exists
    copytree(casedir / "src", tmp_path)
    monkeypatch.chdir(tmp_path)
    r = CliRunner().invoke(main, ["install", "--yes"], standalone_mode=False)
    assert r.exit_code == 0, show_result(r)
    assert_dirtrees_eq(tmp_home, casedir / "dest")
