from __future__ import annotations
from conftest import CaseDirs
from dotplate import Dotplate


def test_simple_templates(simple: CaseDirs) -> None:
    dp = Dotplate.from_config_file(simple.src / "dotplate.toml")
    assert dp.src == simple.src
    assert dp.templates() == [".profile"]


def test_next_to_src_templates(next_to_src: CaseDirs) -> None:
    dp = Dotplate.from_config_file(next_to_src.src / "dotplate.toml")
    assert dp.src == next_to_src.src / "templates"
    assert dp.templates() == [".profile"]
