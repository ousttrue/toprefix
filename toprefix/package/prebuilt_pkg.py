from .pkg import Pkg
from .source import Source
import pathlib
import logging


LOGGER = logging.getLogger(__name__)


class PrebuiltPkg(Pkg):
    def __init__(self, source: Source) -> None:
        self.source = source

    def __str__(self) -> str:
        return f"prebuilt: {self.source}"

    def process(
        self, *, src: pathlib.Path, prefix: pathlib.Path, clean: bool, reconfigure: bool
    ):
        LOGGER.info(f"install: {self}")
        extract = self.source.extract(src)
        assert extract

        # patch
