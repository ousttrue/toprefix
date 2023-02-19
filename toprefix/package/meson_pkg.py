from typing import Optional
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
        LOGGER.info(f"configure: {source_dir} => {env.PREFIX_SRC}")
        with env.pushd(source_dir):
            if not (source_dir / "build").exists():
                env.run( f"meson setup build --prefix {env.PREFIX_SRC}")
            else:
                if clean:
                    shutil.rmtree(source_dir / "build")
                    env.run(
                        f"meson setup build --prefix {env.PREFIX_SRC} {self.args}",
                        env=pkg.make_env(env.PREFIX_SRC),
                    )
                elif reconfigure:
                    env.run(
                        f"meson setup build --prefix {env.PREFIX_SRC} {self.args} --reconfigure",
                        env=pkg.make_env(env.PREFIX_SRC),
                    )

    def build(self, source_dir: pathlib.Path, prefix: pathlib.Path):
        LOGGER.info(f"build: {source_dir} => {prefix}")
        with env.pushd(source_dir):
            env.run(f"meson compile -C build", env=pkg.make_env(prefix))

    def install(self, source_dir: pathlib.Path, prefix: pathlib.Path):
        LOGGER.info(f"install: {source_dir} => {prefix}")
        with env.pushd(source_dir):
            env.run(f"meson install -C build", env=pkg.make_env(prefix))

    def process(self, *, env: EnvMan, clean: bool, reconfigure: bool):
        LOGGER.info(f"install: {self}")
        extract = self.source.extract(env)
        assert extract

        # patch

        # build
        self.configure(extract, env, clean=clean, reconfigure=reconfigure)
        self.build(extract, env.PREFIX_SRC)
        self.install(extract, env.PREFIX_SRC)
