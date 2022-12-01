from typing import Optional
import pathlib
import logging
import shutil
from . import pkg
from .source import Source

LOGGER = logging.getLogger(__name__)


class MesonPkg(pkg.Pkg):
    def __init__(self, source: Source, *, args: str = ''):
        self.source = source
        self.args = args

    def __str__(self) -> str:
        return f"meson: {self.source}"

    def configure(
        self,
        source_dir: pathlib.Path,
        prefix: pathlib.Path,
        *,
        clean: bool,
        reconfigure: bool,
    ):
        LOGGER.info(f"configure: {source_dir} => {prefix}")
        with pkg.pushd(source_dir):
            if not (source_dir / "build").exists():
                pkg.run(
                    f"meson setup build --prefix {prefix}", env=pkg.make_env(prefix)
                )
            else:
                if clean:
                    shutil.rmtree(source_dir / "build")
                    pkg.run(
                        f"meson setup build --prefix {prefix} {self.args}", env=pkg.make_env(prefix)
                    )
                elif reconfigure:
                    pkg.run(
                        f"meson setup build --prefix {prefix} {self.args} --reconfigure",
                        env=pkg.make_env(prefix),
                    )

    def build(self, source_dir: pathlib.Path, prefix: pathlib.Path):
        LOGGER.info(f"build: {source_dir} => {prefix}")
        with pkg.pushd(source_dir):
            pkg.run(f"meson compile -C build", env=pkg.make_env(prefix))

    def install(self, source_dir: pathlib.Path, prefix: pathlib.Path):
        LOGGER.info(f"install: {source_dir} => {prefix}")
        with pkg.pushd(source_dir):
            pkg.run(f"meson install -C build", env=pkg.make_env(prefix))

    def process(
        self, *, src: pathlib.Path, prefix: pathlib.Path, clean: bool, reconfigure: bool
    ):
        LOGGER.info(f"install: {self}")
        extract = self.source.extract(src)
        assert extract

        # patch

        # build
        self.configure(extract, prefix, clean=clean, reconfigure=reconfigure)
        self.build(extract, prefix)
        self.install(extract, prefix)
