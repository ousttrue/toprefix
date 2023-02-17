from typing import Protocol, Optional
import contextlib
import pathlib
import logging
import os
import subprocess
from .source import Source
from ..envman import EnvMan

LOGGER = logging.getLogger(__name__)


@contextlib.contextmanager
def pushd(path: pathlib.Path):
    LOGGER.debug(f"pushd: {path}")
    cwd = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        LOGGER.debug(f"popd: {cwd}")
        os.chdir(cwd)


class Pkg(Protocol):
    source: Source

    def process(self, *, env=EnvMan, clean: bool, reconfigure: bool):
        ...
