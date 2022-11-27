from . import pkg
import pathlib
from .source import Source


class CMakePkg(pkg.Pkg):
    def __init__(self, source: Source) -> None:
        self.source = source

    def __str__(self) -> str:
        return f"cmake: {self.source}"

    def process(
        self, *, src: pathlib.Path, prefix: pathlib.Path, clean: bool, reconfigure: bool
    ):
        raise NotImplementedError()
