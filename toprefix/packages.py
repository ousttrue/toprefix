from typing import Optional, List, Iterable
from .package import Pkg, MesonPkg, CMakePkg, MakePkg, AutoToolsPkg, PrebuiltPkg
from .package.source import Source, Archive, GitRepository
import pkgutil
import pathlib
import toml

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
        case {"autotools": autotools}:
            return AutoToolsPkg(source)
        case {"prebuilt": prebuilt}:
            return PrebuiltPkg(source)
        case _:
            raise NotImplementedError(pkg)


def get_source(name: str, item: dict) -> Source:
    match item["source"]:
        case {"gnome": gnome}:
            return Archive.gnome(name, gnome["version"])
        case {"url": url}:
            return Archive.from_url(url)
        case {"github": repo}:
            match repo:
                case {"user": user, "tag": tag}:
                    return Archive.github_tag(user, name, tag)
                case {"user": user}:
                    return Archive.github_head(user, name)
                case _:
                    raise NotImplementedError()
        case {"codeberg": repo}:
            if "tag" in repo:
                return Archive.codeberg_tag(repo["user"], name, repo["tag"])
            else:
                return GitRepository.github(repo["user"], name)
        case {"sourcehut": repo}:
            if "tag" in repo:
                return Archive.sourcehut_tag(repo["user"], name, repo["tag"])
            else:
                raise NotImplementedError()
        case _:
            raise NotImplementedError()


def iter_patch(dir: pathlib.Path, parsed) -> Iterable[pathlib.Path]:
    match parsed:
        case {"patch": patch}:
            for k, v in patch.items():
                yield dir / v


def generate_pkgs(parsed):
    for k, v in parsed.items():
        source = get_source(k, v)

        for patch in iter_patch(f.parent, v):
            source.patches.append(patch)

        yield make_pkg(v["pkg"], source)


for f in HERE.glob("assets/**/*.toml"):
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
