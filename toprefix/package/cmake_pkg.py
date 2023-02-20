from typing import Optional
import pathlib
import shutil
import logging
from . import pkg
from ..source import Source
from .. import runenv

LOGGER = logging.getLogger(__name__)


class CMakePkg(pkg.Pkg):
    def __init__(
        self, source: Source, *, args: str = "", cmake_source: str = "."
    ) -> None:
        self.source = source
        self.args = args
        self.cmake_source = cmake_source

    def __str__(self) -> str:
        return f"cmake: {self.source}"

    def configure(
        self,
        source_dir: pathlib.Path,
        *,
        clean: bool,
        reconfigure: bool,
    ):
        LOGGER.info(f"configure: {source_dir} => {runenv.PREFIX}")
        with runenv.pushd(source_dir):
            if clean:
                if (source_dir / "build").exists():
                    shutil.rmtree(source_dir / "build")

            runenv.run(
                f"cmake -S {self.cmake_source} -B build -G Ninja -DCMAKE_INSTALL_PREFIX={runenv.PREFIX} -DCMAKE_BUILD_TYPE=Release {self.args}"
            )

    def build(self, source_dir: pathlib.Path):
        LOGGER.info(f"build: {source_dir} => {runenv.PREFIX}")
        with runenv.pushd(source_dir):
            runenv.run(f"cmake --build build")

    def install(self, source_dir: pathlib.Path):
        LOGGER.info(f"install: {source_dir} => {runenv.PREFIX}")
        with runenv.pushd(source_dir):
            runenv.run(f"cmake --install build")

    def process(self, *, clean: bool, reconfigure: bool):
        LOGGER.info(f"install: {self}")
        extract = self.source.extract()
        assert extract

        # patch

        # build
        self.configure(extract, clean=clean, reconfigure=reconfigure)
        self.build(extract)
        self.install(extract)
