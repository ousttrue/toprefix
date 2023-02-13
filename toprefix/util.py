from typing import Protocol, Optional
import contextlib
import pathlib
import logging
import os
import subprocess
from toprefix.source import Source

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


def run(cmd: str, env: Optional[dict]):
    LOGGER.debug(cmd)
    subprocess.run(cmd, env=env, shell=True, check=True)


class Pkg(Protocol):
    source: Source

    def process(
        self, *, src: pathlib.Path, prefix: pathlib.Path, clean: bool, reconfigure: bool
    ):
        ...
