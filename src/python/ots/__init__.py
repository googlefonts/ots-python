import subprocess
import sys
import os

OTS_SANITIZE = os.path.join(os.path.dirname(__file__), "ots-sanitize")


try:
    from ._version import version as __version__
except ImportError:
    __version__ = "0.0.0+unknown"


def sanitize(*args, **kwargs):
    return subprocess.call([OTS_SANITIZE] + list(args), **kwargs)
