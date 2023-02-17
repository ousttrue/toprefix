from . import pkg
from ..source import Source
import pathlib
import logging
from ..envman import EnvMan


LOGGER = logging.getLogger(__name__)


class AutoToolsPkg(pkg.Pkg):
    def __init__(self, source: Source) -> None:
        self.source = source

    def __str__(self) -> str:
        return f"autotools: {self.source}"

    def configure(
        self,
        source_dir: pathlib.Path,
        prefix: pathlib.Path,
        *,
        clean: bool,
        reconfigure: bool,
    ):
        LOGGER.info(f"configure: {source_dir} => {prefix}")
        with util.pushd(source_dir):
            if clean and (source_dir / "Makefile").exists():
                pkg.run(
                    f"make distclean",
                    env=pkg.make_env(prefix),
                )

            pkg.run(
                f"./configure --prefix={prefix}",
                env=pkg.make_env(prefix),
            )

    def build(self, source_dir: pathlib.Path, prefix: pathlib.Path):
        LOGGER.info(f"build: {source_dir} => {prefix}")
        with util.pushd(source_dir):
            pkg.run(f"make", env=pkg.make_env(prefix))

    def install(self, source_dir: pathlib.Path, prefix: pathlib.Path):
        LOGGER.info(f"install: {source_dir} => {prefix}")
        with util.pushd(source_dir):
            pkg.run(f"make install", env=pkg.make_env(prefix))

    def process(self, *, env: EnvMan, clean: bool, reconfigure: bool):
        LOGGER.info(f"install: {self}")
        extract = self.source.extract(src)
        assert extract

        # patch

        # build
        self.configure(extract, prefix, clean=clean, reconfigure=reconfigure)
        self.build(extract, prefix)
        self.install(extract, prefix)
