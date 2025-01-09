from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any
from .config import Config


@dataclass
class Dotplate:
    cfg: Config
    context: dict[str, Any]
    suites: set[str]

    @classmethod
    def from_config(cls, cfg: Config) -> Dotplate:
        raise NotImplementedError

    def src_paths(self) -> list[str]:
        raise NotImplementedError

    def render(self, src_path: str) -> RenderedFile:
        raise NotImplementedError

    def install(self, src_paths: list[str] | None = None) -> None:
        if src_paths is None:
            src_paths = self.src_paths()
        files = [self.render(p) for p in src_paths]
        for f in files:
            f.install()


@dataclass
class RenderedFile:
    content: str
    src_path: str
    dest_path: Path
    executable: bool = False

    def diff(self, dest_path: Path | None) -> Diff:
        raise NotImplementedError

    def install(self, dest_path: Path | None = None) -> None:
        raise NotImplementedError

    def install_in_dir(self, dirpath: Path) -> None:
        raise NotImplementedError


@dataclass
class Diff:
    text: str
    state: DiffState
    xbit_diff: XBitDiff

    def __bool__(self) -> bool:
        return bool(self.state) or bool(self.xbit_diff)


class DiffState(Enum):
    # File is in src but not dest
    MISSING = 1

    # File is in src and dest but content differs
    CHANGED = 2

    # File is in src and dest with identical content
    NODIFF = 3

    def __bool__(self) -> bool:
        return self != DiffState.NODIFF


class XBitDiff(Enum):
    # Executable bit is set on dest file but not src file
    ADDED = 1

    # Executable bit is set on src file but not dest file
    REMOVED = 2

    # Executable bit is the same between files
    NOCHANGE = 3

    def __bool__(self) -> bool:
        return self != XBitDiff.NOCHANGE
