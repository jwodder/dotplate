from __future__ import annotations
from dataclasses import dataclass


class DotplateError(Exception):
    pass


@dataclass
class TemplateNotFound(DotplateError):
    template: str

    def __str__(self) -> str:
        return f"Template not found: {self.template}"


@dataclass
class InactiveTemplate(DotplateError):
    template: str

    def __str__(self) -> str:
        return f"Template is not active: {self.template}"
