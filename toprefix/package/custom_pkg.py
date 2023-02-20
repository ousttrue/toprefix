from . import pkg
from typing import List
from ..source import Source
import logging
from .. import runenv


LOGGER = logging.getLogger(__name__)


class CustomPkg(pkg.Pkg):
    def __init__(self, source: Source, *, commands: List[str]) -> None:
        self.source = source
        self.commands = commands

    def process(self, *, clean: bool, reconfigure: bool):
        extract = self.source.extract()
        assert extract

        LOGGER.info(f"custom: {extract} => {runenv.PREFIX}")
        with runenv.pushd(extract):
            for command in self.commands:
                runenv.run(command)
