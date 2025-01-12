from __future__ import annotations
import shutil
from jinja2 import Environment, Undefined, pass_environment
from jinja2.ext import Extension


class DotplateExt(Extension):
    def __init__(self, env: Environment) -> None:
        env.globals["which"] = which


@pass_environment
def which(env: Environment, *cmds: str) -> str | Undefined:
    for c in cmds:
        if (path := shutil.which(c)) is not None:
            return path
    return env.undefined("which() could not locate any commands")
