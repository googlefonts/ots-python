from __future__ import absolute_import, unicode_literals
import pytest
import subprocess
import ots


def test_sanitize():
    p = ots.sanitize()
    assert p.returncode == 1
    assert len(p.args) == 1
    assert p.args[0].endswith("ots-sanitize")
    assert p.stdout == None
    assert p.stderr == None


def test_check_error():
    with pytest.raises(subprocess.CalledProcessError):
        ots.sanitize("--foo", "bar", check=True)


def test_capture_output():
    p = ots.sanitize(capture_output=True)
    assert len(p.stdout) == 0
    stderr = p.stderr.decode()
    assert stderr.startswith("Usage: ")
