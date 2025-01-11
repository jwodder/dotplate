from __future__ import annotations
from pathlib import Path
import shutil
from dotplate import Dotplate

DATA_DIR = Path(__file__).with_name("data")


def test_simple_templates(tmp_path: Path) -> None:
    shutil.copytree(
        DATA_DIR / "examples" / "simple" / "src", tmp_path, dirs_exist_ok=True
    )
    dp = Dotplate.from_config_file(tmp_path / "dotplate.toml")
    assert dp.src == tmp_path
    assert dp.templates() == [".profile"]
