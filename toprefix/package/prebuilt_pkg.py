from typing import Optional
import os
from .pkg import Pkg
from ..source import Source
import pathlib
import logging
import shutil
from .. import runenv

LOGGER = logging.getLogger(__name__)


class PrebuiltPkg(Pkg):
    def __init__(self, source: Source, *, install: Optional[dict] = None) -> None:
        self.source = source
        self.install = install or {}

    def __str__(self) -> str:
        return f"prebuilt: {self.source}"

    def process(self, *, clean: bool, reconfigure: bool):
        LOGGER.info(f"install: {self}")
        extract = self.source.extract()
        assert extract

        bin = self.install.get("bin")
        if bin:
            src: pathlib.Path = extract / bin
            dst: pathlib.Path = runenv.LOCAL_BIN / bin
            if dst.is_file() or dst.is_symlink():
                os.remove(dst)
                LOGGER.info(f"overwrite: {src} => {dst}")
            else:
                LOGGER.info(f"link: {src} => {dst}")
            dst.symlink_to(src)
