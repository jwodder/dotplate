from __future__ import annotations
import argparse
from collections.abc import Sequence
from enum import Enum
from pathlib import Path
import sys
from typing import Any
from . import __version__
from .config import Config, LocalConfig
from .dotplate import Dotplate, RenderedFile

try:
    import readline  # noqa: F401
except ImportError:
    pass

DEFAULT_CONFIG_PATH = Path("dotplate.toml")


class EnableSuite(argparse.Action):
    def __call__(
        self,
        _parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        value: str | Sequence[Any] | None,
        _option_string: str | None = None,
    ) -> None:
        if not isinstance(value, str):
            raise TypeError(value)  # pragma: no cover
        enabled = getattr(namespace, "suites_enabled", {})
        enabled[value] = True
        namespace.suites_enabled = enabled


class DisableSuite(argparse.Action):
    def __call__(
        self,
        _parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        value: str | Sequence[Any] | None,
        _option_string: str | None = None,
    ) -> None:
        if not isinstance(value, str):
            raise TypeError(value)  # pragma: no cover
        enabled = getattr(namespace, "suites_enabled", {})
        enabled[value] = False
        namespace.suites_enabled = enabled


def main(argv: list[str] | None = None) -> None:
    (dotplate, ns) = parse_args(argv)
    match ns.cmd:
        case "diff":
            diff(dotplate, ns.templates)
        case "install":
            install(dotplate, ns.templates, yes=ns.yes)
        case "list":
            list_cmd(dotplate)
        case "render":
            render(dotplate, ns.template)
        case _:
            raise RuntimeError(f"Unhandled subcommand: {ns.cmd!r}")


def parse_args(argv: list[str] | None = None) -> tuple[Dotplate, argparse.Namespace]:
    parser = argparse.ArgumentParser(
        description="Yet another dotfile manager/templater",
        epilog=(
            "Visit <https://github.com/jwodder/dotplate> or"
            " <https://dotplate.rtfd.io> for more information."
        ),
    )
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        metavar="PATH",
        help=(
            "Read the primary config from the given file"
            f"  [default: {DEFAULT_CONFIG_PATH}]"
        ),
    )
    parser.add_argument(
        "-d",
        "--dest",
        type=Path,
        metavar="DIRPATH",
        help="Install templated files in the given directory  [default: set by config]",
    )
    parser.add_argument(
        "-l",
        "--local-config",
        type=Path,
        metavar="PATH",
        help="Read the local config from the given file  [default: set by config]",
    )
    parser.add_argument(
        "-s",
        "--enable-suite",
        action=EnableSuite,
        metavar="SUITE",
        help="Enable the given suite of files",
    )
    parser.add_argument(
        "-S",
        "--disable-suite",
        action=DisableSuite,
        metavar="SUITE",
        help="Disable the given suite of files",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    subparsers = parser.add_subparsers(dest="cmd")
    install = subparsers.add_parser(
        "install",
        help=(
            "Render & install the given templates in the destination directory.\n"
            "\n"
            "If no templates are given on the command line, all active templates are\n"
            "diffed."
        ),
    )
    install.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Install all active templates without prompting for confirmation",
    )
    install.add_argument("templates", nargs="*")
    diff = subparsers.add_parser(
        "diff",
        help=(
            "Render each template and output a diff between the rendered text and the\n"
            "contents of the corresponding file in the destination directory.  If a\n"
            "given render matches the installed file, nothing is output.\n"
            "\n"
            "If no templates are given on the command line, all active templates are\n"
            "diffed."
        ),
    )
    diff.add_argument("templates", nargs="*")
    subparsers.add_parser("list", help="List all active templates")
    render = subparsers.add_parser(
        "render", help="Render the given template and output the resulting text"
    )
    render.add_argument("template")
    ns = parser.parse_args(argv)
    cfg = Config.from_file(ns.config)
    if ns.local_config is None:
        cfg.load_local_config()
    else:
        lccfg = LocalConfig.from_file(ns.local_config)
        cfg.merge_local_config(lccfg)
    if ns.dest is not None:
        cfg.core.dest = ns.dest
    for name, enable in getattr(ns, "suites_enabled", {}).items():
        try:
            cfg.suites[name].enabled = enable
        except KeyError:
            pass
    dotplate = Dotplate.from_config(cfg)
    return (dotplate, ns)


def diff(dotplate: Dotplate, templates: list[str]) -> None:
    if not templates:
        templates = dotplate.templates()
    for sp in templates:
        file = dotplate.render(sp)
        d = file.diff()
        if d.state:
            print(d.delta, end="")


def install(dotplate: Dotplate, templates: list[str], yes: bool) -> None:
    if not templates:
        templates = dotplate.templates()
    files = [dotplate.render(p) for p in templates]
    for f in files:
        if not f.diff():
            continue
        if yes:
            action = PromptAction.YES
        else:
            action = install_prompt(f)
            if action is PromptAction.ALL:
                yes = True
                action = PromptAction.YES
        if action is PromptAction.YES:
            f.install()
            print(f"Installed {f.template} at {f.dest_path}")
        elif action is PromptAction.QUIT:
            break


def list_cmd(dotplate: Dotplate) -> None:
    for sp in dotplate.templates():
        print(sp)


def render(dotplate: Dotplate, template: str) -> None:
    f = dotplate.render(template)
    print(f.content, end="")


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
            sys.exit(1)
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


if __name__ == "__main__":
    main()  # pragma: no cover
