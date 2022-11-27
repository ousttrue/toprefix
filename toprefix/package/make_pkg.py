import pathlib
import logging
from . import pkg
from .source import Source


LOGGER = logging.getLogger(__name__)


class MakePkg(pkg.Pkg):
    def __init__(self, source: Source) -> None:
        self.source = source

    def __str__(self) -> str:
        return f"make: {self.source}"

    def process(
        self, *, src: pathlib.Path, prefix: pathlib.Path, clean: bool, reconfigure: bool
    ):
        LOGGER.info(f"install: {self}")
        extract = self.source.extract(src)
        assert extract

        # patch

        # build
        # self.configure(extract, prefix, clean=clean, reconfigure=reconfigure)
        self.build(extract, prefix)
        self.install(extract, prefix)

    def build(self, source_dir: pathlib.Path, prefix: pathlib.Path):
        LOGGER.info(f"build: {source_dir} => {prefix}")
        with pkg.pushd(source_dir):
            pkg.run(f"make", env=pkg.make_env(prefix))

    def install(self, source_dir: pathlib.Path, prefix: pathlib.Path):
        LOGGER.info(f"install: {source_dir} => {prefix}")
        with pkg.pushd(source_dir):
            pkg.run(f"make install", env=pkg.make_env(prefix))
