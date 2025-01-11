from __future__ import annotations
import os
from pathlib import Path
import shutil
import pytest
from dotplate import DiffState, Dotplate, XBitDiff
from dotplate.util import set_executable_bit, unset_executable_bit

DATA_DIR = Path(__file__).with_name("data")

unix_only = pytest.mark.skipif(
    os.name != "posix", reason="Windows doesn't support executability"
)


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


def test_simple_changed(tmp_home: Path, tmp_path: Path) -> None:
    shutil.copytree(
        DATA_DIR / "examples" / "simple" / "src", tmp_path, dirs_exist_ok=True
    )
    dp = Dotplate.from_config_file(tmp_path / "dotplate.toml")
    (tmp_home / ".profile").write_text(
        'export PATH="$PATH:$HOME/local/bin"\nexport EDITOR=vim\n'
    )
    rf = dp.render(".profile")
    diff = rf.diff()
    assert bool(diff)
    assert diff.delta == (
        "--- .profile\n"
        f"+++ {tmp_home / '.profile'}\n"
        "@@ -1,2 +1,2 @@\n"
        '-export PATH="$PATH:$HOME/local/bin"\n'
        '+export PATH="$PATH:$HOME/local/bin:$HOME/.cargo/bin"\n'
        " export EDITOR=vim\n"
    )
    assert diff.state is DiffState.CHANGED
    assert diff.xbit_diff is XBitDiff.NOCHANGE


def test_simple_missing(tmp_home: Path, tmp_path: Path) -> None:
    shutil.copytree(
        DATA_DIR / "examples" / "simple" / "src", tmp_path, dirs_exist_ok=True
    )
    dp = Dotplate.from_config_file(tmp_path / "dotplate.toml")
    rf = dp.render(".profile")
    diff = rf.diff()
    assert bool(diff)
    assert diff.delta == (
        "--- .profile\n"
        f"+++ {tmp_home / '.profile'}\n"
        "@@ -0,0 +1,2 @@\n"
        '+export PATH="$PATH:$HOME/local/bin:$HOME/.cargo/bin"\n'
        "+export EDITOR=vim\n"
    )
    assert diff.state is DiffState.MISSING
    assert diff.xbit_diff is XBitDiff.NOCHANGE


@unix_only
def test_simple_xbit_added(tmp_home: Path, tmp_path: Path) -> None:
    shutil.copytree(
        DATA_DIR / "examples" / "simple" / "src", tmp_path, dirs_exist_ok=True
    )
    dp = Dotplate.from_config_file(tmp_path / "dotplate.toml")
    shutil.copyfile(
        DATA_DIR / "examples" / "simple" / "dest" / ".profile", tmp_home / ".profile"
    )
    set_executable_bit(tmp_home / ".profile")
    rf = dp.render(".profile")
    diff = rf.diff()
    assert bool(diff)
    assert diff.delta == "old mode +x\nnew mode -x\n"
    assert diff.state is DiffState.NODIFF
    assert diff.xbit_diff is XBitDiff.ADDED


@unix_only
def test_simple_changed_xbit_added(tmp_home: Path, tmp_path: Path) -> None:
    shutil.copytree(
        DATA_DIR / "examples" / "simple" / "src", tmp_path, dirs_exist_ok=True
    )
    dp = Dotplate.from_config_file(tmp_path / "dotplate.toml")
    (tmp_home / ".profile").write_text(
        'export PATH="$PATH:$HOME/local/bin"\nexport EDITOR=vim\n'
    )
    set_executable_bit(tmp_home / ".profile")
    rf = dp.render(".profile")
    diff = rf.diff()
    assert bool(diff)
    assert diff.delta == (
        "old mode +x\n"
        "new mode -x\n"
        "--- .profile\n"
        f"+++ {tmp_home / '.profile'}\n"
        "@@ -1,2 +1,2 @@\n"
        '-export PATH="$PATH:$HOME/local/bin"\n'
        '+export PATH="$PATH:$HOME/local/bin:$HOME/.cargo/bin"\n'
        " export EDITOR=vim\n"
    )
    assert diff.state is DiffState.CHANGED
    assert diff.xbit_diff is XBitDiff.ADDED


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


@unix_only
def test_script_xbit_removed(tmp_home: Path, tmp_path: Path) -> None:
    shutil.copytree(
        DATA_DIR / "examples" / "script" / "src", tmp_path, dirs_exist_ok=True
    )
    dp = Dotplate.from_config_file(tmp_path / "dotplate.toml")
    (tmp_home / "bin").mkdir()
    shutil.copy(
        DATA_DIR / "examples" / "script" / "dest" / "bin" / "flavoring",
        tmp_home / "bin" / "flavoring",
    )
    unset_executable_bit(tmp_home / "bin" / "flavoring")
    rf = dp.render("bin/flavoring")
    diff = rf.diff()
    assert bool(diff)
    assert diff.delta == "old mode -x\nnew mode +x\n"
    assert diff.state is DiffState.NODIFF
    assert diff.xbit_diff is XBitDiff.REMOVED


@unix_only
def test_script_changed_xbit_removed(tmp_home: Path, tmp_path: Path) -> None:
    shutil.copytree(
        DATA_DIR / "examples" / "script" / "src", tmp_path, dirs_exist_ok=True
    )
    dp = Dotplate.from_config_file(tmp_path / "dotplate.toml")
    (tmp_home / "bin").mkdir()
    (tmp_home / "bin" / "flavoring").write_text(
        "#!/bin/bash\n" "printf 'Who likes %s?\\n' 'cinnamon'\n"
    )
    rf = dp.render("bin/flavoring")
    diff = rf.diff()
    assert bool(diff)
    assert diff.delta == (
        "old mode -x\n"
        "new mode +x\n"
        "--- bin/flavoring\n"
        f"+++ {tmp_home / 'bin' / 'flavoring'}\n"
        "@@ -1,2 +1,2 @@\n"
        " #!/bin/bash\n"
        "-printf 'Who likes %s?\\n' 'cinnamon'\n"
        "+printf 'Who likes %s?\\n' 'licorice'\n"
    )
    assert diff.state is DiffState.CHANGED
    assert diff.xbit_diff is XBitDiff.REMOVED


@unix_only
def test_script_missing(tmp_home: Path, tmp_path: Path) -> None:
    shutil.copytree(
        DATA_DIR / "examples" / "script" / "src", tmp_path, dirs_exist_ok=True
    )
    dp = Dotplate.from_config_file(tmp_path / "dotplate.toml")
    rf = dp.render("bin/flavoring")
    diff = rf.diff()
    assert bool(diff)
    assert diff.delta == (
        "new file mode +x\n"
        "--- bin/flavoring\n"
        f"+++ {tmp_home / 'bin' / 'flavoring'}\n"
        "@@ -0,0 +1,2 @@\n"
        "+#!/bin/bash\n"
        "+printf 'Who likes %s?\\n' 'licorice'\n"
    )
    assert diff.state is DiffState.MISSING
    assert diff.xbit_diff is XBitDiff.NOCHANGE
