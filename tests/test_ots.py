import pytest
import ots


def test_sanitize():
    assert ots.sanitize() == 1
