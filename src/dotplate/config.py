from __future__ import annotations
from collections import defaultdict
from collections.abc import Callable
from pathlib import Path
import sys
from typing import Annotated, Any, Literal
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import BaseModel, Field
from pydantic.functional_validators import AfterValidator
from .jinja_ext import DotplateExt
from .util import SuiteSet

if sys.version_info[:2] >= (3, 11):
    from tomllib import load as toml_load
else:
    from tomli import load as toml_load


def expandpath(p: Path) -> Path:
    return p.expanduser()


ExpandedPath = Annotated[Path, AfterValidator(expandpath)]


def mkalias(s: str) -> str:
    return s.replace("_", "-")


class BaseConfig(BaseModel):
    model_config = {
        "alias_generator": mkalias,
        "populate_by_name": True,
        "extra": "forbid",
    }


class CoreConfig(BaseConfig):
    src: ExpandedPath = Field(default_factory=Path)
    dest: ExpandedPath
    local_config: ExpandedPath | None = None
    backup_ext: str = Field(default=".dotplate.bak", min_length=1)

    def resolve_paths_relative_to(self, p: Path) -> None:
        self.src = p / self.src
        self.dest = p / self.dest
        if self.local_config is not None:
            self.local_config = p / self.local_config


class SelectAutoescapeConfig(BaseConfig):
    enabled_extensions: list[str] = Field(
        default_factory=lambda: ["html", "htm", "xml"]
    )
    disabled_extensions: list[str] = Field(default_factory=list)
    default: bool = False

    def get(self) -> Callable[[str | None], bool]:
        return select_autoescape(
            enabled_extensions=self.enabled_extensions,
            disabled_extensions=self.disabled_extensions,
            default=self.default,
        )


class JinjaConfig(BaseConfig):
    block_start_string: str = "{%"
    block_end_string: str = "%}"
    variable_start_string: str = "{{"
    variable_end_string: str = "}}"
    comment_start_string: str = "{#"
    comment_end_string: str = "#}"
    line_statement_prefix: str | None = None
    line_comment_prefix: str | None = None
    trim_blocks: bool = False
    lstrip_blocks: bool = False
    newline_sequence: Literal["\n", "\r\n", "\r"] = "\n"
    keep_trailing_newline: bool = False
    extensions: list[str] = Field(default_factory=list)
    optimized: bool = True
    autoescape: bool | None = None
    select_autoescape: SelectAutoescapeConfig = Field(
        default_factory=SelectAutoescapeConfig
    )
    cache_size: int = 400
    auto_reload: bool = True

    def get_autoescape(self) -> bool | Callable[[str | None], bool]:
        if self.autoescape is None:
            return self.select_autoescape.get()
        else:
            return self.autoescape


class SuiteConfig(BaseConfig):
    files: list[str]
    enabled: bool = False


class Config(BaseConfig):
    core: CoreConfig
    jinja: JinjaConfig = Field(default_factory=JinjaConfig)
    suites: dict[str, SuiteConfig] = Field(default_factory=dict)
    vars: dict[str, Any] = Field(default_factory=dict)
    _exclude_config_path: str | None = None

    @classmethod
    def from_file(cls, filepath: str | Path) -> Config:
        with open(filepath, "rb") as fp:
            data = toml_load(fp)
        cfg = cls.model_validate(data)
        cfg.resolve_paths_relative_to(Path(filepath).parent)
        src = cfg.core.src.resolve()
        cfgpath = Path(filepath).resolve()
        try:
            cfg._exclude_config_path = cfgpath.relative_to(src).as_posix()
        except ValueError:
            pass
        return cfg

    def merge_local_config(self, cfg: LocalConfig) -> None:
        if cfg.local.dest is not None:
            self.core.dest = cfg.local.dest
        if isinstance(cfg.local.enabled_suites, list):
            enabled = set(cfg.local.enabled_suites)
            for name, suicfg in self.suites.items():
                suicfg.enabled = name in enabled
        elif isinstance(cfg.local.enabled_suites, dict):
            for name, enable in cfg.local.enabled_suites.items():
                try:
                    self.suites[name].enabled = enable
                except KeyError:
                    pass
        if cfg.vars is not None:
            self.vars.update(cfg.vars)

    def load_local_config(self) -> None:
        if self.core.local_config is not None:
            try:
                cfg = LocalConfig.from_file(self.core.local_config)
            except FileNotFoundError:
                return
            self.merge_local_config(cfg)

    def resolve_paths_relative_to(self, p: Path) -> None:
        self.core.resolve_paths_relative_to(p)

    def default_suites(self) -> set[str]:
        return {name for name, suicfg in self.suites.items() if suicfg.enabled}

    def paths2suites(self) -> defaultdict[str, SuiteSet]:
        mapping: defaultdict[str, SuiteSet] = defaultdict(SuiteSet)
        for name, suicfg in self.suites.items():
            for file in suicfg.files:
                mapping[file].suites.add(name)
        return mapping

    def make_jinja_env(self) -> Environment:
        return Environment(
            loader=FileSystemLoader(self.core.src, followlinks=True),
            block_start_string=self.jinja.block_start_string,
            block_end_string=self.jinja.block_end_string,
            variable_start_string=self.jinja.variable_start_string,
            variable_end_string=self.jinja.variable_end_string,
            comment_start_string=self.jinja.comment_start_string,
            comment_end_string=self.jinja.comment_end_string,
            line_statement_prefix=self.jinja.line_statement_prefix,
            line_comment_prefix=self.jinja.line_comment_prefix,
            trim_blocks=self.jinja.trim_blocks,
            lstrip_blocks=self.jinja.lstrip_blocks,
            newline_sequence=self.jinja.newline_sequence,
            keep_trailing_newline=self.jinja.keep_trailing_newline,
            extensions=[DotplateExt, *self.jinja.extensions],
            optimized=self.jinja.optimized,
            autoescape=self.jinja.get_autoescape(),
            cache_size=self.jinja.cache_size,
            auto_reload=self.jinja.auto_reload,
        )


class LocalTblConfig(BaseConfig):
    dest: ExpandedPath | None = None
    enabled_suites: list[str] | dict[str, bool] | None = None


class LocalConfig(BaseConfig):
    local: LocalTblConfig
    vars: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_file(cls, filepath: str | Path) -> LocalConfig:
        with open(filepath, "rb") as fp:
            data = toml_load(fp)
        cfg = cls.model_validate(data)
        return cfg
