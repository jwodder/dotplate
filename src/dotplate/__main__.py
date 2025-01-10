from __future__ import annotations
from pathlib import Path
import click
from . import __version__
from .config import Config, LocalConfig
from .dotplate import Dotplate

DEFAULT_CONFIG_PATH = Path("dotplate.toml")


def enable_suite(ctx: click.Context, _param: click.Parameter, value: str) -> str:
    ctx.params.setdefault("suites_enabled", {})[value] = True
    return value


def disable_suite(ctx: click.Context, _param: click.Parameter, value: str) -> str:
    ctx.params.setdefault("suites_enabled", {})[value] = False
    return value


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "-c",
    "--config",
    type=click.Path(exists=True, dir_okay=False, readable=True, path_type=Path),
    default=DEFAULT_CONFIG_PATH,
)
@click.option("-d", "--dest", type=click.Path(file_okay=False, path_type=Path))
@click.option(
    "-l",
    "--local-config",
    type=click.Path(exists=True, dir_okay=False, readable=True, path_type=Path),
)
@click.option(
    "-s", "--enable-suite", multiple=True, callback=enable_suite, expose_value=False
)
@click.option(
    "-S", "--disable-suite", multiple=True, callback=disable_suite, expose_value=False
)
@click.version_option(
    __version__,
    "-V",
    "--version",
    message="%(prog)s %(version)s",
)
@click.pass_context
def main(
    ctx: click.Context,
    config: Path,
    dest: Path | None,
    local_config: Path | None,
    suites_enabled: dict[str, bool] | None = None,
) -> None:
    """
    Yet another dotfile manager/templater

    Visit <https://github.com/jwodder/dotplate> or <https://dotplate.rtfd.io> for
    more information.
    """
    cfg = Config.from_file(config)
    if local_config is None:
        cfg.load_local_config()
    else:
        lccfg = LocalConfig.from_file(local_config)
        cfg.merge_local_config(lccfg)
    if dest is not None:
        cfg.core.dest = dest
    if suites_enabled is not None:
        for name, enable in suites_enabled.items():
            try:
                cfg.suites[name].enabled = enable
            except KeyError:
                pass
    ctx.obj = Dotplate.from_config(cfg)


@main.command()
@click.argument("src_paths", nargs=-1)
@click.pass_obj
def diff(dotplate: Dotplate, src_paths: tuple[str, ...]) -> None:
    if not src_paths:
        src_paths = tuple(dotplate.src_paths())
    for sp in src_paths:
        file = dotplate.render(sp)
        d = file.diff()
        ### TODO: Report differences in executable bit
        if d.state:
            print(d.delta)


@main.command()
@click.argument("src_paths", nargs=-1)
@click.pass_obj
def install(dotplate: Dotplate, src_paths: tuple[str, ...]) -> None:
    if not src_paths:
        src_paths = tuple(dotplate.src_paths())
    dotplate.install(list(src_paths) or None)


@main.command("list")
@click.pass_obj
def list_cmd(dotplate: Dotplate) -> None:
    for sp in dotplate.src_paths():
        print(sp)


if __name__ == "__main__":
    main()  # pragma: no cover
