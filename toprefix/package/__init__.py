from typing import List, Iterable, Optional
import pathlib
import toml
from ..source import get_source, Source
from .pkg import Pkg
from .meson_pkg import MesonPkg
from .cmake_pkg import CMakePkg
from .make_pkg import MakePkg
from .autotools_pkg import AutoToolsPkg
from .prebuilt_pkg import PrebuiltPkg
from .custom_pkg import CustomPkg

HERE = pathlib.Path(__file__).absolute().parent
PKGS: List[Pkg] = []


def make_pkg(pkg: str, source: Source) -> Pkg:
    match pkg:
        case {"meson": meson}:
            return MesonPkg(source, **meson)
        case {"cmake": cmake}:
            return CMakePkg(source, **cmake)
        case {"make": make}:
            return MakePkg(source, **make)
        case {"autotools": _}:
            return AutoToolsPkg(source)
        # case {"bazel": bazel}:
        #     return BazelPkg(source)
        case {"prebuilt": prebuilt}:
            return PrebuiltPkg(source, **prebuilt)
        case {"custom": commands}:
            return CustomPkg(source, commands=commands.split("\n"))
        case _:
            raise NotImplementedError(pkg)


def iter_patch(dir: pathlib.Path, parsed) -> Iterable[pathlib.Path]:
    match parsed:
        case {"patch": patch}:
            for _, v in patch.items():
                yield dir / v


def generate_pkgs(parsed):
    for k, v in parsed.items():
        source = get_source(k, v)

        # for patch in iter_patch(f.parent, v):
        #     source.patches.append(patch)
        yield make_pkg(v["pkg"], source)


def init_pkgs():
    for f in HERE.parent.glob("assets/**/*.toml"):
        if f.is_file and f.suffix == ".toml":
            data = f.read_text(encoding="utf-8")
            parsed = toml.loads(data)
            for pkg in generate_pkgs(parsed):
                PKGS.append(pkg)


def list_pkgs():
    for pkg in PKGS:
        print(pkg)


def get_pkg(name: str) -> Optional[Pkg]:
    for pkg in PKGS:
        if pkg.source.name == name:
            return pkg
