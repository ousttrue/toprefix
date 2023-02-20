import pathlib
import logging
import shutil
from .pkg import Pkg
from ..source import Source
from ..envman import EnvMan

LOGGER = logging.getLogger(__name__)


class MesonPkg(Pkg):
    def __init__(self, source: Source, *, args: str = ""):
        self.source = source
        self.args = args

    def __str__(self) -> str:
        return f"meson: {self.source}"

    def configure(
        self,
        source_dir: pathlib.Path,
        env: EnvMan,
        *,
        clean: bool,
        reconfigure: bool,
    ):
        LOGGER.info(f"configure: {source_dir} => {env.PREFIX}")
        with env.pushd(source_dir):
            if not (source_dir / "build").exists():
                env.run(f"meson setup build --prefix {env.PREFIX}")
            else:
                if clean:
                    shutil.rmtree(source_dir / "build")
                    env.run(f"meson setup build --prefix {env.PREFIX} {self.args}")
                elif reconfigure:
                    env.run(
                        f"meson setup build --prefix {env.PREFIX} {self.args} --reconfigure"
                    )

    def build(self, source_dir: pathlib.Path, env: EnvMan):
        LOGGER.info(f"build: {source_dir} => {env.PREFIX}")
        with env.pushd(source_dir):
            env.run(f"meson compile -C build")

    def install(self, source_dir: pathlib.Path, env: EnvMan):
        LOGGER.info(f"install: {source_dir} => {env.PREFIX}")
        with env.pushd(source_dir):
            env.run(f"meson install -C build")

    def process(self, *, env: EnvMan, clean: bool, reconfigure: bool):
        LOGGER.info(f"install: {self}")
        extract = self.source.extract(env)
        assert extract

        # patch

        # build
        self.configure(extract, env, clean=clean, reconfigure=reconfigure)
        self.build(extract, env)
        self.install(extract, env)
