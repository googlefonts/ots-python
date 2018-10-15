import pytest
import ots


def test_sanitize():
    p = ots.sanitize()
    assert p.returncode == 1
    assert len(p.args) == 1
    assert p.args[0].endswith("ots-sanitize")
    assert p.stdout == None
    assert p.stderr == None
