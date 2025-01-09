from __future__ import annotations
from collections import defaultdict
from pathlib import Path
import sys
from typing import Annotated, Any
from pydantic import BaseModel, Field
from pydantic.functional_validators import AfterValidator
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


class PathConfig(BaseConfig):
    src: ExpandedPath
    dest: ExpandedPath
    local_config: ExpandedPath | None = None

    def resolve_paths_relative_to(self, p: Path) -> None:
        self.src = p / self.src
        self.dest = p / self.dest
        if self.local_config is not None:
            self.local_config = p / self.local_config


class SuiteConfig(BaseConfig):
    files: list[str]
    enabled: bool = False


class Config(BaseConfig):
    paths: PathConfig
    # TODO: jinja
    suites: dict[str, SuiteConfig] = Field(default_factory=dict)
    # TODO: vars

    @classmethod
    def from_file(cls, filepath: str | Path) -> Config:
        with open(filepath, "rb") as fp:
            data = toml_load(fp)
        cfg = cls.model_validate(data)
        cfg.resolve_paths_relative_to(Path(filepath).parent)
        return cfg

    def resolve_paths_relative_to(self, p: Path) -> None:
        self.paths.resolve_paths_relative_to(p)

    def default_suites(self) -> set[str]:
        return {name for name, suicfg in self.suites.items() if suicfg.enabled}

    def context(self) -> dict[str, Any]:
        raise NotImplementedError

    def paths2suites(self) -> defaultdict[str, SuiteSet]:
        mapping: defaultdict[str, SuiteSet] = defaultdict(SuiteSet)
        for name, suicfg in self.suites.items():
            for file in suicfg.files:
                mapping[file].suites.add(name)
        return mapping


# TODO: Local config
