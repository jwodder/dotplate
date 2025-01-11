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
from .errors import InactiveTemplate, TemplateNotFound
from .util import (
    SuiteSet,
    backup,
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
    # Templates are in sorted order:
    _templates: list[tuple[str, SuiteSet]] | None = field(init=False, default=None)

    @classmethod
    def from_config_file(cls, cfgfile: str | Path) -> Dotplate:
        cfg = Config.from_file(cfgfile)
        cfg.load_local_config()
        return cls.from_config(cfg)

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

    def _ensure_templates(self) -> list[tuple[str, SuiteSet]]:
        if self._templates is None:
            suitemap = self.cfg.paths2suites()
            templates = listdir(self.src)
            # listdir() should return the paths in sorted order, but just to be
            # sure…
            templates.sort()
            if self.cfg._exclude_config_path is not None:
                try:
                    templates.remove(self.cfg._exclude_config_path)
                except ValueError:
                    pass
            self._templates = [(path, suitemap[path]) for path in templates]
        return self._templates

    def templates(self) -> list[str]:
        templates = self._ensure_templates()
        return [
            path
            for (path, suiteset) in templates
            if suiteset.is_file_active(self.suites)
        ]

    def is_active(self, template: str) -> bool:
        templates = self._ensure_templates()
        if not templates:
            raise TemplateNotFound(template)
        i = bisect_left(templates, template, key=itemgetter(0))
        (sp, suiteset) = templates[i]
        if sp != template:
            raise TemplateNotFound(template)
        return suiteset.is_file_active(self.suites)

    def render(self, template: str, dest_path: Path | None = None) -> RenderedFile:
        if not self.is_active(template):
            raise InactiveTemplate(template)
        tmplobj = self.jinja_env.get_template(template)
        if dest_path is None:
            dest_path = self.dest / template
        return RenderedFile(
            content=tmplobj.render(
                self.get_context(template=template, dest_path=dest_path)
            )
            + "\n",
            template=template,
            executable=is_executable(self.src / template),
            dest_path=dest_path,
            backup_ext=self.cfg.core.backup_ext,
        )

    def install_path(self, template: str, dest_path: Path | None = None) -> None:
        self.render(template, dest_path).install()

    def install(self, templates: list[str] | None = None) -> None:
        if templates is None:
            templates = self.templates()
        files = [self.render(p) for p in templates]
        for f in files:
            f.install()

    def get_context(self, template: str, dest_path: Path) -> dict[str, Any]:
        # Returns a fresh dict on each invocation
        return {
            "dotplate": {
                "suites": {
                    name: {
                        "files": suicfg.files,
                        "enabled": name in self.suites,
                    }
                    for name, suicfg in self.cfg.suites.items()
                },
                "template": template,
                "dest_path": str(dest_path),
                "vars": self.vars.copy(),
            }
        }


@dataclass
class RenderedFile:
    content: str
    template: str
    dest_path: Path
    backup_ext: str
    executable: bool = False
    _diff: Diff | None = field(init=False, default=None)

    def diff(self) -> Diff:
        if self._diff is None:
            try:
                with self.dest_path.open("r", encoding="utf-8") as fp:
                    dest_content = fp.read()
            except FileNotFoundError:
                dest_content = ""
                state = DiffState.MISSING
                xbit_diff = XBitDiff.NOCHANGE
            else:
                state = (
                    DiffState.NODIFF
                    if dest_content == self.content
                    else DiffState.CHANGED
                )
                match (self.executable, is_executable(self.dest_path)):
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
                    fromfile=self.template,
                    tofile=str(self.dest_path),
                )
            )
            self._diff = Diff(delta=delta, state=state, xbit_diff=xbit_diff)
        return self._diff

    def install(self) -> None:
        if diff := self.diff():
            if diff.state:
                backup(self.dest_path, self.backup_ext)
                self.dest_path.parent.mkdir(parents=True, exist_ok=True)
                with self.dest_path.open("w", encoding="utf-8") as fp:
                    fp.write(self.content)
            if self.executable:
                set_executable_bit(self.dest_path)
            else:
                unset_executable_bit(self.dest_path)


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
