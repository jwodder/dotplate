from __future__ import annotations
from pathlib import Path
import shutil
from dotplate import DiffState, Dotplate, XBitDiff

DATA_DIR = Path(__file__).with_name("data")


def test_simple_nodiff(tmp_home: Path, tmp_path: Path) -> None:
    shutil.copytree(
        DATA_DIR / "examples" / "simple" / "src", tmp_path, dirs_exist_ok=True
    )
    dp = Dotplate.from_config_file(tmp_path / "dotplate.toml")
    shutil.copyfile(
        DATA_DIR / "examples" / "simple" / "dest" / ".profile", tmp_home / ".profile"
    )
    rf = dp.render(".profile")
    diff = rf.diff()
    assert not bool(diff)
    assert diff.delta == ""
    assert diff.state is DiffState.NODIFF
    assert diff.xbit_diff is XBitDiff.NOCHANGE


def test_simple_diff(tmp_home: Path, tmp_path: Path) -> None:
    shutil.copytree(
        DATA_DIR / "examples" / "simple" / "src", tmp_path, dirs_exist_ok=True
    )
    dp = Dotplate.from_config_file(tmp_path / "dotplate.toml")
    (tmp_home / ".profile").write_text(
        'export PATH="$PATH:$HOME/local/bin"\n' "export EDITOR=vim\n"
    )
    rf = dp.render(".profile")
    diff = rf.diff()
    assert bool(diff)
    assert diff.delta == (
        "--- .profile\n"
        f"+++ {tmp_home}/.profile\n"
        "@@ -1,2 +1,2 @@\n"
        '-export PATH="$PATH:$HOME/local/bin"\n'
        '+export PATH="$PATH:$HOME/local/bin:$HOME/.cargo/bin"\n'
        " export EDITOR=vim\n"
    )
    assert diff.state is DiffState.CHANGED
    assert diff.xbit_diff is XBitDiff.NOCHANGE


def test_simple_missing_diff(tmp_home: Path, tmp_path: Path) -> None:
    shutil.copytree(
        DATA_DIR / "examples" / "simple" / "src", tmp_path, dirs_exist_ok=True
    )
    dp = Dotplate.from_config_file(tmp_path / "dotplate.toml")
    rf = dp.render(".profile")
    diff = rf.diff()
    assert bool(diff)
    assert diff.delta == (
        "--- .profile\n"
        f"+++ {tmp_home}/.profile\n"
        "@@ -0,0 +1,2 @@\n"
        '+export PATH="$PATH:$HOME/local/bin:$HOME/.cargo/bin"\n'
        "+export EDITOR=vim\n"
    )
    assert diff.state is DiffState.MISSING
    assert diff.xbit_diff is XBitDiff.NOCHANGE


def test_script_nodiff(tmp_home: Path, tmp_path: Path) -> None:
    shutil.copytree(
        DATA_DIR / "examples" / "script" / "src", tmp_path, dirs_exist_ok=True
    )
    dp = Dotplate.from_config_file(tmp_path / "dotplate.toml")
    (tmp_home / "bin").mkdir()
    shutil.copy(
        DATA_DIR / "examples" / "script" / "dest" / "bin" / "flavoring",
        tmp_home / "bin" / "flavoring",
    )
    rf = dp.render("bin/flavoring")
    diff = rf.diff()
    assert not bool(diff)
    assert diff.delta == ""
    assert diff.state is DiffState.NODIFF
    assert diff.xbit_diff is XBitDiff.NOCHANGE
