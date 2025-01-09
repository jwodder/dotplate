from __future__ import annotations
from bisect import bisect_left
from dataclasses import dataclass, field
from difflib import unified_diff
from enum import Enum
from operator import itemgetter
from pathlib import Path
from typing import Any
from jinja2 import Environment
from .config import Config
from .errors import InactiveSrcPath, SrcPathNotFound
from .util import (
    SuiteSet,
    is_executable,
    listdir,
    set_executable_bit,
    unset_executable_bit,
)


@dataclass
class Dotplate:
    cfg: Config
    vars: dict[str, Any]
    suites: set[str]
    jinja_env: Environment
    dest: Path
    # Src paths are in sorted order:
    _src_paths: list[tuple[str, SuiteSet]] | None = field(init=False, default=None)

    @classmethod
    def from_config_file(cls, cfgfile: str | Path) -> Dotplate:
        return cls.from_config(Config.from_file(cfgfile))

    @classmethod
    def from_config(cls, cfg: Config) -> Dotplate:
        uservars = cfg.vars.copy()
        suites = cfg.default_suites()
        jinja_env = cfg.make_jinja_env()
        return cls(
            cfg=cfg,
            vars=uservars,
            suites=suites,
            jinja_env=jinja_env,
            dest=cfg.core.dest,
        )

    @property
    def src(self) -> Path:
        return self.cfg.core.src

    def _ensure_src_paths(self) -> list[tuple[str, SuiteSet]]:
        if self._src_paths is None:
            suitemap = self.cfg.paths2suites()
            src_paths = listdir(self.dest)
            # listdir() should return the paths in sorted order, but just to be
            # sure…
            src_paths.sort()
            self._src_paths = [(path, suitemap[path]) for path in src_paths]
        return self._src_paths

    def src_paths(self) -> list[str]:
        src_paths = self._ensure_src_paths()
        return [
            path
            for (path, suiteset) in src_paths
            if suiteset.is_file_active(self.suites)
        ]

    def is_active(self, src_path: str) -> bool:
        src_paths = self._ensure_src_paths()
        if not src_paths:
            raise SrcPathNotFound(src_path)
        i = bisect_left(src_paths, src_path, key=itemgetter(0))
        (sp, suiteset) = src_paths[i]
        if sp != src_path:
            raise SrcPathNotFound(src_path)
        return suiteset.is_file_active(self.suites)

    def render(self, src_path: str, dest_path: Path | None = None) -> RenderedFile:
        if not self.is_active(src_path):
            raise InactiveSrcPath(src_path)
        template = self.jinja_env.get_template(src_path)
        if dest_path is None:
            dest_path = self.dest / src_path
        return RenderedFile(
            content=template.render(self.get_context(dest_path)),
            src_path=src_path,
            executable=is_executable(self.src / src_path),
            dest_path=dest_path,
        )

    def install_path(self, src_path: str, dest_path: Path | None = None) -> None:
        self.render(src_path, dest_path).install()

    def install(self, src_paths: list[str] | None = None) -> None:
        if src_paths is None:
            src_paths = self.src_paths()
        files = [self.render(p) for p in src_paths]
        for f in files:
            f.install()

    def get_context(self, dest_path: Path) -> dict[str, Any]:
        # Returs a fresh dict on each invocation
        return {
            "dotplate": {
                "suites": {
                    "enabled": sorted(self.suites),
                    "files": {
                        name: list(suicfg.files)
                        for name, suicfg in self.cfg.suites.items()
                    },
                },
                "dest_path": str(dest_path),
                "vars": self.vars.copy(),
            }
        }


@dataclass
class RenderedFile:
    content: str
    src_path: str
    dest_path: Path
    executable: bool = False

    def diff(self, dest_path: Path | None) -> Diff:
        if dest_path is None:
            dest_path = self.dest_path
        try:
            with dest_path.open("r", encoding="utf-8") as fp:
                dest_content = fp.read()
        except FileNotFoundError:
            dest_content = ""
            state = DiffState.MISSING
            xbit_diff = XBitDiff.REMOVED if self.executable else XBitDiff.NOCHANGE
        else:
            state = (
                DiffState.NODIFF if dest_content == self.content else DiffState.CHANGED
            )
            match (self.executable, is_executable(dest_path)):
                case (True, False):
                    xbit_diff = XBitDiff.REMOVED
                case (False, True):
                    xbit_diff = XBitDiff.ADDED
                case _:
                    xbit_diff = XBitDiff.NOCHANGE
        delta = "".join(
            unified_diff(
                dest_content.splitlines(True),
                self.content.splitlines(True),
                fromfile=self.src_path,
                tofile=str(dest_path),
            )
        )
        return Diff(delta=delta, state=state, xbit_diff=xbit_diff)

    def install(self, dest_path: Path | None = None) -> None:
        if dest_path is None:
            dest_path = self.dest_path
        if diff := self.diff(dest_path):
            if diff.state:
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                with dest_path.open("w", encoding="utf-8") as fp:
                    fp.write(self.content)
            if diff.xbit_diff:
                if self.executable:
                    set_executable_bit(dest_path)
                else:
                    unset_executable_bit(dest_path)

    def install_in_dir(self, dirpath: Path) -> None:
        self.install(dirpath / self.src_path)


@dataclass
class Diff:
    delta: str
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
