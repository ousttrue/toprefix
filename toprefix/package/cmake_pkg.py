from typing import Optional
import pathlib
import shutil
import logging
from . import pkg
from .source import Source


LOGGER = logging.getLogger(__name__)


class CMakePkg(pkg.Pkg):
    def __init__(self, source: Source, *, args: str = "") -> None:
        self.source = source
        self.args = args

    def __str__(self) -> str:
        return f"cmake: {self.source}"

    def configure(
        self,
        source_dir: pathlib.Path,
        prefix: pathlib.Path,
        *,
        clean: bool,
        reconfigure: bool,
    ):
        LOGGER.info(f"configure: {source_dir} => {prefix}")
        with pkg.pushd(source_dir):
            if clean:
                if (source_dir / "build").exists():
                    shutil.rmtree(source_dir / "build")

            pkg.run(
                f"cmake -S . -B build -G Ninja -DCMAKE_INSTALL_PREFIX={prefix} -DCMAKE_BUILD_TYPE=Release {self.args}",
                env=pkg.make_env(prefix),
            )

    def build(self, source_dir: pathlib.Path, prefix: pathlib.Path):
        LOGGER.info(f"build: {source_dir} => {prefix}")
        with pkg.pushd(source_dir):
            pkg.run(f"cmake --build build", env=pkg.make_env(prefix))

    def install(self, source_dir: pathlib.Path, prefix: pathlib.Path):
        LOGGER.info(f"install: {source_dir} => {prefix}")
        with pkg.pushd(source_dir):
            pkg.run(f"cmake --install build", env=pkg.make_env(prefix))

    def process(
        self, *, src: pathlib.Path, prefix: pathlib.Path, clean: bool, reconfigure: bool
    ):
        LOGGER.info(f"install: {self}")
        extract = self.source.extract(src)
        assert extract

        # patch

        # build
        self.configure(extract, prefix, clean=clean, reconfigure=reconfigure)
        self.build(extract, prefix)
        self.install(extract, prefix)
