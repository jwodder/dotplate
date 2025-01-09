from __future__ import annotations
from pathlib import Path
import sys
from typing import Annotated
from pydantic import BaseModel
from pydantic.functional_validators import AfterValidator

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


class Config(BaseConfig):
    paths: PathConfig
    # TODO: jinja
    # TODO: suites
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


# TODO: Local config
