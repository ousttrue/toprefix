from typing import Optional, List
from .package import Pkg, MesonPkg, CMakePkg, MakePkg, AutoToolsPkg, PrebuiltPkg
from .package.source import Source, Archive, GitRepository
import pkgutil
import toml

PKGS: List[Pkg] = []


def make_pkg(pkg: str, source: Source) -> Pkg:
    match pkg:
        case {"meson": meson}:
            return MesonPkg(source, **meson)
        case {"cmake": cmake}:
            return CMakePkg(source, **cmake)
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
            if "tag" in repo:
                return Archive.github_tag(repo["user"], name, repo["tag"])
            else:
                return GitRepository.github(repo["user"], name)
        case {"codeberg": repo}:
            if "tag" in repo:
                return Archive.codeberg_tag(repo["user"], name, repo["tag"])
            else:
                return GitRepository.github(repo["user"], name)
        case _:
            raise NotImplementedError()


def generate_pkgs(parsed):
    for k, v in parsed.items():
        source = get_source(k, v)
        yield make_pkg(v["pkg"], source)


data = pkgutil.get_data("toprefix", "assets/packages.toml")
if data:
    parsed = toml.loads(data.decode("utf-8"))
    for pkg in generate_pkgs(parsed):
        PKGS.append(pkg)


def list_pkgs():
    for pkg in PKGS:
        print(pkg)


def get_pkg(name: str) -> Optional[Pkg]:
    for pkg in PKGS:
        if pkg.source.name == name:
            return pkg
