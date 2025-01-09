from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import stat
import subprocess
from iterpath import iterpath
from linesep import split_terminated


@dataclass
class SuiteSet:
    suites: set[str] = field(default_factory=set)

    def is_file_active(self, enabled_suites: set[str]) -> bool:
        return not self.suites or bool(self.suites & enabled_suites)


def listdir(dirpath: Path) -> list[str]:
    """
    List the files in `dirpath`, relative to `dirpath` and
    forward-slash-separated.  If `dirpath` is in a Git repository, only files
    known to Git are returned.
    """
    if in_git(dirpath):
        # TODO: Try to include files staged but not yet committed
        # (Merge a variant of `git diff --cached --name-status`?)
        r = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", "-z"],
            cwd=dirpath,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return split_terminated(r.stdout, "\0")
    else:
        with iterpath(dirpath, dirs=False, return_relative=True, sort=True) as ip:
            return [str(p) for p in ip]


def in_git(dirpath: Path) -> bool:
    """Test whether `dirpath` is under Git revision control"""
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=dirpath,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        if r.stdout.strip() == "false":
            # We are inside a .git directory
            return False
    except FileNotFoundError:
        # Git not installed; assume this isn't a Git repository
        return False
    except subprocess.CalledProcessError:
        return False
    # Check whether `path` is tracked by Git (Note that we can't rely
    # on this check alone, as it succeeds when inside a .git/ directory)
    return (
        subprocess.run(
            ["git", "ls-files", "--error-unmatch", "."],
            cwd=dirpath,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode
        == 0
    )


def is_executable(p: Path) -> bool:
    return p.stat().st_mode & stat.S_IXUSR != 0


def set_executable_bit(p: Path) -> None:
    mode = p.stat().st_mode
    mode |= stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    p.chmod(mode)


def unset_executable_bit(p: Path) -> None:
    mode = p.stat().st_mode
    mode &= ~(stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    p.chmod(mode)
