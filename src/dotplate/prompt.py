from __future__ import annotations
from enum import Enum
import click
from .dotplate import RenderedFile


class PromptAction(Enum):
    YES = 1
    NO = 2
    ALL = 3
    QUIT = 4


def install_prompt(rf: RenderedFile) -> PromptAction:
    while True:
        try:
            print(f"Install {rf.template} at {rf.dest_path}?")
            r = input("[(y)es/(n)o/(a)ll/(d)iff/(q)uit] ")
        except KeyboardInterrupt:
            raise click.Abort()
        match r.lower():
            case "y" | "yes":
                return PromptAction.YES
            case "n" | "no":
                return PromptAction.NO
            case "d" | "diff":
                print(rf.diff().delta)
            case "a" | "all":
                return PromptAction.ALL
            case "q" | "quit":
                return PromptAction.QUIT
