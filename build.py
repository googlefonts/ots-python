#!/usr/bin/env python3
"""Run meson and ninja to build the ots-sanitize executable from source.

NOTE: This script requires Python 3.6 or above. However the generated binary
is independent from the python version used to run it.
"""
import sys
import platform
import enum
from pathlib import Path
import os
import subprocess
import shutil
import errno
import argparse


class MacTarget(enum.Enum):
    X86_64 = "x86_64"
    ARM64 = "arm64"
    UNIVERSAL2 = "universal2"


PLATFORM = platform.uname()

ROOT = Path(__file__).parent.resolve()
SRC_DIR = ROOT.joinpath("src", "c", "ots")
DEFAULT_BUILD_DIR = ROOT / "build" / "meson"

CROSS_FILES_DIR = ROOT / "cross-files"
MACOS_CROSS_FILES = {
    MacTarget.ARM64: CROSS_FILES_DIR / "darwin" / "arm64",
    MacTarget.X86_64: CROSS_FILES_DIR / "darwin" / "x86_64",
}

TOOLS = {
    "meson": os.environ.get("MESON_EXE", "meson"),
    "ninja": os.environ.get("NINJA_EXE", "ninja"),
}

MESON_OPTIONS = [
    "--backend=ninja",
    "--buildtype=release",
    "--strip",
    "-Ddebug=true",
]
if PLATFORM.system == "Windows":
    MESON_OPTIONS.append("--force-fallback-for=zlib")

if PLATFORM.system == "Darwin":
    MESON_OPTIONS.append("--force-fallback-for=google-brotli,lz4")

    native_machine = MacTarget(PLATFORM.machine)
    cross_machine = (
        MacTarget.ARM64 if native_machine == MacTarget.X86_64 else MacTarget.X86_64
    )
    MACOS_CROSS_FILES = {
        native_machine: [""],
        cross_machine: [MACOS_CROSS_FILES[cross_machine]],
    }
    MACOS_CROSS_FILES[MacTarget.UNIVERSAL2] = (
        MACOS_CROSS_FILES[MacTarget.X86_64] + MACOS_CROSS_FILES[MacTarget.ARM64]
    )


class ExecutableNotFound(FileNotFoundError):
    def __init__(self, name, path):
        msg = f"{name} executable not found: '{path}'"
        super().__init__(errno.ENOENT, msg)


def check_tools():
    for name, path in TOOLS.items():
        if shutil.which(path) is None:
            raise ExecutableNotFound(name, path)


def configure(build_dir, reconfigure=False, cross_file=""):
    meson_cmd = [TOOLS["meson"]] + MESON_OPTIONS + [str(build_dir), str(SRC_DIR)]
    if cross_file:
        meson_cmd.insert(1, f"--cross-file={cross_file}")
    if not (build_dir / "build.ninja").exists():
        subprocess.run(meson_cmd, check=True, env=os.environ)
    elif reconfigure:
        subprocess.run(meson_cmd + ["--reconfigure"], check=True, env=os.environ)


def make(build_dir, *targets, clean=False):
    ninja_cmd = [TOOLS["ninja"], "-C", str(build_dir)]
    targets = list(targets)
    if clean:
        subprocess.run(
            ninja_cmd + ["-t", "clean"] + targets, check=True, env=os.environ
        )
    subprocess.run(ninja_cmd + targets, check=True, env=os.environ)


def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--force", action="store_true")
    parser.add_argument("--build-dir", default=DEFAULT_BUILD_DIR, type=Path)
    parser.add_argument(
        "--mac-target",
        default=None,
        metavar="ARCH",
        type=MacTarget,
        help=(f"{(', ').join(v.value for v in MacTarget)}"),
    )
    parser.add_argument("targets", nargs="*")
    options = parser.parse_args(args)

    check_tools()

    build_dirs = [options.build_dir]
    cross_files = [""]

    if options.mac_target is not None:
        if PLATFORM.system == "Darwin":
            cross_files = MACOS_CROSS_FILES[options.mac_target]
            if options.mac_target == MacTarget.UNIVERSAL2:
                build_dirs = [options.build_dir / arch for arch in ("x86_64", "arm64")]
        else:
            print(
                "WARNING: --mac-target option is ignored on non-mac platforms",
                file=sys.stderr,
            )

    for cross_file, build_dir in zip(cross_files, build_dirs):
        try:
            configure(
                build_dir,
                reconfigure=options.force,
                cross_file=cross_file,
            )

            make(build_dir, *options.targets, clean=options.force)
        except subprocess.CalledProcessError as e:
            return e.returncode

    if options.mac_target == MacTarget.UNIVERSAL2:
        # create universal binary by merging multiple archs with the 'lipo' tool:
        # https://developer.apple.com/documentation/apple-silicon/building-a-universal-macos-binary
        for filename in options.targets:
            arch_paths = [
                options.build_dir / arch / filename for arch in ("x86_64", "arm64")
            ]
            dest_path = options.build_dir / filename
            subprocess.run(
                ["lipo", "-create", "-output", dest_path] + arch_paths,
                check=True,
                env=os.environ,
            )
            # confirm that we got a 'fat' binary
            result = subprocess.run(
                ["lipo", "-archs", dest_path], check=True, capture_output=True
            )
            assert "x86_64 arm64" == result.stdout.decode().strip()


if __name__ == "__main__":
    sys.exit(main())
