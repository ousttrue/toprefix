from typing import Optional
import pathlib
import logging
from . import pkg
from ..source import Source
from .. import runenv

LOGGER = logging.getLogger(__name__)


class MakePkg(pkg.Pkg):
    def __init__(self, source: Source, *, args: str) -> None:
        self.source = source
        self.args = args

    def __str__(self) -> str:
        return f"make: {self.source}"

    def process(
        self, *, clean: bool, reconfigure: bool
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
        pass
        # LOGGER.info(f"build: {source_dir} => {prefix}")
        # with util.pushd(source_dir):
        #     pkg.run(f"make {self.args}", env=pkg.make_env(prefix))

    def install(self, source_dir: pathlib.Path, prefix: pathlib.Path):
        LOGGER.info(f"install: {source_dir} => {prefix}")
        with util.pushd(source_dir):
            pkg.run(f"make {self.args}", env=pkg.make_env(prefix))
