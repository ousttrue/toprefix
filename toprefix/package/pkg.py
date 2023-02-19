from typing import Protocol
import logging
from ..source import Source
from ..envman import EnvMan

LOGGER = logging.getLogger(__name__)


class Pkg(Protocol):
    source: Source

    def process(self, *, env: EnvMan, clean: bool, reconfigure: bool):
        ...

# class Pkg(Protocol):
#     source: Source

#     def process(
#         self, *, src: pathlib.Path, prefix: pathlib.Path, clean: bool, reconfigure: bool
#     ):
#         ...
