import subprocess
import sys
import os

OTS_SANITIZE = os.path.join(os.path.dirname(__file__), "ots-sanitize")


def sanitize(args=None):
    if args is None:
        args = sys.argv[1:]
    return subprocess.call([OTS_SANITIZE] + args)
