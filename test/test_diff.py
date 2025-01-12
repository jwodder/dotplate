from __future__ import annotations
import os
from pathlib import Path
import shutil
from conftest import CaseDirs
import pytest
from dotplate import DiffState, Dotplate, XBitDiff
from dotplate.util import set_executable_bit, unset_executable_bit

unix_only = pytest.mark.skipif(
    os.name != "posix", reason="Windows doesn't support executability"
)


@pytest.mark.usecase("simple")
def test_simple_nodiff(tmp_home: Path, casedirs: CaseDirs) -> None:
    dp = Dotplate.from_config_file(casedirs.src / "dotplate.toml")
    shutil.copyfile(casedirs.dest / ".profile", tmp_home / ".profile")
    rf = dp.render(".profile")
    diff = rf.diff()
    assert not bool(diff)
    assert diff.delta == ""
    assert diff.state is DiffState.NODIFF
    assert diff.xbit_diff is XBitDiff.NOCHANGE


@pytest.mark.usecase("simple")
def test_simple_changed(tmp_home: Path, casedirs: CaseDirs) -> None:
    dp = Dotplate.from_config_file(casedirs.src / "dotplate.toml")
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


@pytest.mark.usecase("simple")
def test_simple_missing(tmp_home: Path, casedirs: CaseDirs) -> None:
    dp = Dotplate.from_config_file(casedirs.src / "dotplate.toml")
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
    assert diff.xbit_diff is XBitDiff.MISSING_UNSET


@unix_only
@pytest.mark.usecase("simple")
def test_simple_xbit_added(tmp_home: Path, casedirs: CaseDirs) -> None:
    dp = Dotplate.from_config_file(casedirs.src / "dotplate.toml")
    shutil.copyfile(casedirs.dest / ".profile", tmp_home / ".profile")
    set_executable_bit(tmp_home / ".profile")
    rf = dp.render(".profile")
    diff = rf.diff()
    assert bool(diff)
    assert diff.delta == "old mode +x\nnew mode -x\n"
    assert diff.state is DiffState.NODIFF
    assert diff.xbit_diff is XBitDiff.ADDED


@unix_only
@pytest.mark.usecase("simple")
def test_simple_changed_xbit_added(tmp_home: Path, casedirs: CaseDirs) -> None:
    dp = Dotplate.from_config_file(casedirs.src / "dotplate.toml")
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


@pytest.mark.usecase("script")
def test_script_nodiff(tmp_home: Path, casedirs: CaseDirs) -> None:
    dp = Dotplate.from_config_file(casedirs.src / "dotplate.toml")
    (tmp_home / "bin").mkdir()
    shutil.copy(
        casedirs.dest / "bin" / "flavoring",
        tmp_home / "bin" / "flavoring",
    )
    rf = dp.render("bin/flavoring")
    diff = rf.diff()
    assert not bool(diff)
    assert diff.delta == ""
    assert diff.state is DiffState.NODIFF
    assert diff.xbit_diff is XBitDiff.NOCHANGE


@unix_only
@pytest.mark.usecase("script")
def test_script_xbit_removed(tmp_home: Path, casedirs: CaseDirs) -> None:
    dp = Dotplate.from_config_file(casedirs.src / "dotplate.toml")
    (tmp_home / "bin").mkdir()
    shutil.copy(
        casedirs.dest / "bin" / "flavoring",
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
@pytest.mark.usecase("script")
def test_script_changed_xbit_removed(tmp_home: Path, casedirs: CaseDirs) -> None:
    dp = Dotplate.from_config_file(casedirs.src / "dotplate.toml")
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
@pytest.mark.usecase("script")
def test_script_missing(tmp_home: Path, casedirs: CaseDirs) -> None:
    dp = Dotplate.from_config_file(casedirs.src / "dotplate.toml")
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
    assert diff.xbit_diff is XBitDiff.MISSING_SET
