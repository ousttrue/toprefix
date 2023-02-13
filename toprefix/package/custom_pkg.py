from . import pkg
from .source import Source
import pathlib
import logging
import shutil


LOGGER = logging.getLogger(__name__)


class CustomPkg(pkg.Pkg):
    def __init__(self, source: Source) -> None:
        self.source = source

    def process(
        self, *, src: pathlib.Path, prefix: pathlib.Path, clean: bool, reconfigure: bool
    ):
        pass

