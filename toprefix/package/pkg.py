from typing import Protocol
import logging
from ..source import Source

LOGGER = logging.getLogger(__name__)


class Pkg(Protocol):
    source: Source

    def process(self, *, clean: bool, reconfigure: bool):
        ...


# class Pkg(Protocol):
#     source: Source

#     def process(
#         self, *, src: pathlib.Path, prefix: pathlib.Path, clean: bool, reconfigure: bool
#     ):
#         ...
