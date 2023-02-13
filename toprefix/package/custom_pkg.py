from . import pkg
from typing import List
from .source import Source
import pathlib
import logging
import shutil


LOGGER = logging.getLogger(__name__)


class CustomPkg(pkg.Pkg):
    def __init__(self, source: Source, *, commands: List[str]) -> None:
        self.source = source
        self.commands = commands

    def process(
        self, *, src: pathlib.Path, prefix: pathlib.Path, clean: bool, reconfigure: bool
    ):
        extract = self.source.extract(src)
        assert extract

        LOGGER.info(f"custom: {extract} => {prefix}")
        with pkg.pushd(extract):
            for command in self.commands:
                pkg.run(
                    command.format(PREFIX=prefix),
                    env=pkg.make_env(prefix),
                )
