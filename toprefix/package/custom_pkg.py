from . import pkg
from typing import List
from .source import Source
import pathlib
import logging
from ..envman import EnvMan


LOGGER = logging.getLogger(__name__)


class CustomPkg(pkg.Pkg):
    def __init__(self, source: Source, *, commands: List[str]) -> None:
        self.source = source
        self.commands = commands

    def process(self, *, env: EnvMan, clean: bool, reconfigure: bool):
        extract = self.source.extract(env.PREFIX_SRC)
        assert extract

        LOGGER.info(f"custom: {extract} => {env.PREFIX}")
        with pkg.pushd(extract):
            for command in self.commands:
                env.run(command)
