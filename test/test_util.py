from __future__ import annotations
import os
from pathlib import Path
import pytest
from dotplate.util import is_executable, set_executable_bit, unset_executable_bit


@pytest.mark.skipif(os.name != "posix", reason="Windows doesn't support executability")
def test_executable_bit(tmp_path: Path) -> None:
    p = tmp_path / "foo.txt"
    p.write_text("Now this file exists.\n")
    assert not is_executable(p)
    set_executable_bit(p)
    assert is_executable(p)
    unset_executable_bit(p)
    assert not is_executable(p)
