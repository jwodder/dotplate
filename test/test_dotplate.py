from __future__ import annotations
from pathlib import Path
from shutil import copytree
from dotplate import Dotplate

DATA_DIR = Path(__file__).with_name("data")


def test_simple(tmp_path: Path) -> None:
    tmp_path /= "tmp"  # copytree() can't copy to a dir that already exists
    copytree(DATA_DIR / "end2end" / "simple" / "src", tmp_path)
    dp = Dotplate.from_config_file(tmp_path / "dotplate.toml")
    assert dp.src == tmp_path
    assert dp.templates() == [".profile"]
