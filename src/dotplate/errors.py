from __future__ import annotations
from dataclasses import dataclass


class DotplateError(Exception):
    pass


@dataclass
class SrcPathNotFound(DotplateError):
    src_path: str

    def __str__(self) -> str:
        return f"No such src path: {self.src_path}"


@dataclass
class InactiveSrcPath(DotplateError):
    src_path: str

    def __str__(self) -> str:
        return f"src path is not active: {self.src_path}"
