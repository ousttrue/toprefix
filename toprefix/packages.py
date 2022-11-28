from typing import Optional, List
from .package import Pkg, MesonPkg, CMakePkg, MakePkg, PrebuiltPkg
from .package.source import Source, Archive, GitRepository
import pkgutil
import toml

PKGS: List[Pkg] = []


def make_pkg(pkg: str, source: Source) -> Pkg:
    match pkg:
        case "meson":
            return MesonPkg(source)
        case "prebuilt":
            return PrebuiltPkg(source)
        case _:
            raise NotImplementedError(pkg)


def pkgs_url(items):
    for item in items:
        yield make_pkg(item["pkg"], Archive.from_url(item["url"]))


def pkgs_gnome(items):
    for item in items:
        source = Archive.gnome(
            name=item["name"],
            major=item["major"],
            minor=item["minor"],
            patch=item["patch"],
        )
        yield make_pkg(item["pkg"], source)


def pkgs_github(items):
    for item in items:
        if "tag" in item:
            source = Archive.github_tag(item["user"], item["name"], item["tag"])
        else:
            source = GitRepository.github(item["user"], item["name"])
        yield make_pkg(item["pkg"], source)


def pkgs_codeberg(items):
    for item in items:
        if "tag" in item:
            source = Archive.codeberg_tag(item["user"], item["name"], item["tag"])
        else:
            raise NotImplementedError()
        yield make_pkg(item["pkg"], source)


def generate_pkgs(parsed):
    for k, v in parsed.items():
        match k:
            case "url":
                for pkg in pkgs_url(v):
                    yield pkg
            case "gnome":
                for pkg in pkgs_gnome(v):
                    yield pkg
            case "github":
                for pkg in pkgs_github(v):
                    yield pkg
            case "codeberg":
                for pkg in pkgs_codeberg(v):
                    yield pkg
            case _:
                raise NotImplementedError(k)


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
