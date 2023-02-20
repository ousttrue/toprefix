from . import pkg
from ..source import Source
import pathlib
import logging
from ..envman import EnvMan


LOGGER = logging.getLogger(__name__)


class BazelPkg(pkg.Pkg):
    def __init__(self, source: Source) -> None:
        self.source = source

    def process(self, *, env: EnvMan, clean: bool, reconfigure: bool):
        pass

