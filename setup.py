from __future__ import print_function, absolute_import
from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext
from distutils.file_util import copy_file
from distutils.dir_util import mkpath
from distutils import log
import os
import sys
import subprocess

if sys.version_info[:2] < (3, 6):
    sys.exit(
        "error: Python 3.6 is required to run setup.py. \n"
        "The generated wheel will be compatible with both py27 and py3+"
    )


cmdclass = {}
try:
    from wheel.bdist_wheel import bdist_wheel
except ImportError:
    pass
else:

    class UniversalBdistWheel(bdist_wheel):
        def get_tag(self):
            return ("py2.py3", "none") + bdist_wheel.get_tag(self)[2:]

    cmdclass["bdist_wheel"] = UniversalBdistWheel


class Executable(Extension):

    if os.name == "nt":
        suffix = ".exe"
    else:
        suffix = ""

    def __init__(self, name, script, output_dir=".", cwd=None, env=None):
        Extension.__init__(self, name, sources=[])
        self.target = self.name.split(".")[-1]
        self.script = script
        self.output_dir = output_dir
        self.cwd = cwd
        self.env = env


class ExecutableBuildExt(build_ext):
    def get_ext_filename(self, ext_name):
        for ext in self.extensions:
            if isinstance(ext, Executable):
                return os.path.join(*ext_name.split(".")) + ext.suffix
        return build_ext.get_ext_filename(self, ext_name)

    def build_extension(self, ext):
        if not isinstance(ext, Executable):
            build_ext.build_extension(self, ext)
            return

        cmd = [sys.executable, ext.script, ext.target]
        if self.force:
            cmd += ["--force"]
        log.debug("running '{}'".format(" ".join(cmd)))
        if not self.dry_run:
            p = subprocess.run(cmd, cwd=ext.cwd, env=ext.env)
            if p.returncode != 0:
                from distutils.errors import DistutilsExecError

                raise DistutilsExecError(
                    "running '{}' script failed".format(ext.script)
                )

        exe_name = ext.target + ext.suffix
        exe_fullpath = os.path.join(ext.output_dir, exe_name)

        dest_path = self.get_ext_fullpath(ext.name)
        mkpath(os.path.dirname(dest_path), verbose=self.verbose, dry_run=self.dry_run)

        copy_file(exe_fullpath, dest_path, verbose=self.verbose, dry_run=self.dry_run)


cmdclass["build_ext"] = ExecutableBuildExt

ots_sanitize = Executable(
    "ots.ots-sanitize", script="build.py", output_dir=os.path.join("build", "meson")
)

with open("README.md", "r", encoding="utf-8") as readme:
    long_description = readme.read()

setup(
    name="opentype-sanitizer",
    use_scm_version=True,
    description=("Python wrapper for the OpenType Sanitizer"),
    long_description=long_description,
    author="Cosimo Lupo",
    author_email="cosimo@anthrotype.com",
    url="https://github.com/anthrotype/ots-python",
    license="MIT",
    platforms=["posix", "nt"],
    package_dir={"": "src/python"},
    packages=find_packages("src/python"),
    ext_modules=[ots_sanitize],
    zip_safe=False,
    cmdclass=cmdclass,
    setup_requires=["setuptools_scm"],
    extras_require={"testing": ["pytest"]},
    entry_points={"console_scripts": ["ots-sanitize = ots:sanitize"]},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Text Processing :: Fonts",
        "Topic :: Multimedia :: Graphics",
    ],
)
