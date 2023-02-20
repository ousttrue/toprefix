import pathlib
import logging
import shutil
from .pkg import Pkg
from ..source import Source
from .. import runenv

LOGGER = logging.getLogger(__name__)


class MesonPkg(Pkg):
    def __init__(self, source: Source, *, args: str = ""):
        meson = runenv.which("meson")
        if not meson:
            raise Exception("meson not found")
        self.meson = meson
        self.source = source
        self.args = args

    def __str__(self) -> str:
        return f"meson: {self.source}"

    def configure(
        self,
        source_dir: pathlib.Path,
        *,
        clean: bool,
        reconfigure: bool,
    ):
        LOGGER.info(f"configure: {source_dir} => {runenv.PREFIX}")
        with runenv.pushd(source_dir):
            if not (source_dir / "build").exists():
                runenv.run(f"{self.meson} setup build --prefix {runenv.PREFIX}")
            else:
                if clean:
                    shutil.rmtree(source_dir / "build")
                    runenv.run(
                        f"{self.meson} setup build --prefix {runenv.PREFIX} {self.args}"
                    )
                elif reconfigure:
                    runenv.run(
                        f"{self.meson} setup build --prefix {runenv.PREFIX} {self.args} --reconfigure"
                    )

    def build(self, source_dir: pathlib.Path):
        LOGGER.info(f"build: {source_dir} => {runenv.PREFIX}")
        with runenv.pushd(source_dir):
            runenv.run(f"{self.meson} compile -C build")

    def install(self, source_dir: pathlib.Path):
        LOGGER.info(f"install: {source_dir} => {runenv.PREFIX}")
        with runenv.pushd(source_dir):
            runenv.run(f"{self.meson} install -C build")

    def process(self, *, clean: bool, reconfigure: bool):
        LOGGER.info(f"install: {self}")
        extract = self.source.extract()
        assert extract

        # build
        self.configure(extract, clean=clean, reconfigure=reconfigure)
        self.build(extract)
        self.install(extract)
