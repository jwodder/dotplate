from __future__ import annotations
from pathlib import Path
import shutil
from dotplate import DiffState, Dotplate, XBitDiff

DATA_DIR = Path(__file__).with_name("data")


def test_simple_templates(tmp_path: Path) -> None:
    tmp_path /= "tmp"  # copytree() can't copy to a dir that already exists
    shutil.copytree(DATA_DIR / "examples" / "simple" / "src", tmp_path)
    dp = Dotplate.from_config_file(tmp_path / "dotplate.toml")
    assert dp.src == tmp_path
    assert dp.templates() == [".profile"]


def test_simple_nodiff(tmp_home: Path, tmp_path: Path) -> None:
    tmp_path /= "tmp"  # copytree() can't copy to a dir that already exists
    shutil.copytree(DATA_DIR / "examples" / "simple" / "src", tmp_path)
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
    tmp_path /= "tmp"  # copytree() can't copy to a dir that already exists
    shutil.copytree(DATA_DIR / "examples" / "simple" / "src", tmp_path)
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
    tmp_path /= "tmp"  # copytree() can't copy to a dir that already exists
    shutil.copytree(DATA_DIR / "examples" / "simple" / "src", tmp_path)
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
