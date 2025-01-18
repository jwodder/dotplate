from __future__ import annotations
from conftest import CaseDirs
import pytest
from dotplate import Dotplate


@pytest.mark.usecase("simple")
def test_simple_templates(casedirs: CaseDirs) -> None:
    dp = Dotplate.from_config_file(casedirs.src / "dotplate.toml")
    assert dp.src == casedirs.src
    assert dp.templates() == [".profile"]


@pytest.mark.usecase("next-to-src")
def test_next_to_src_templates(casedirs: CaseDirs) -> None:
    dp = Dotplate.from_config_file(casedirs.src / "dotplate.toml")
    assert dp.src == casedirs.src / "templates"
    assert dp.templates() == [".profile"]


@pytest.mark.usecase("suited")
def test_suited_templates(casedirs: CaseDirs) -> None:
    dp = Dotplate.from_config_file(casedirs.src / "dotplate.toml")
    assert dp.src == casedirs.src
    assert dp.templates() == [".profile"]
    dp.suites.add("vim")
    assert dp.templates() == [".profile", ".vimrc"]
