import os
import pytest
unix_only = pytest.mark.skipif(
    os.name != "posix", reason="Windows doesn't support executability"
)

    assert diff.xbit_diff is XBitDiff.MISSING_UNSET
@unix_only
@unix_only
@unix_only
@unix_only
@unix_only
    assert diff.xbit_diff is XBitDiff.MISSING_SET