from typing import Optional, List
from .package import Pkg, MesonPkg, CMakePkg
from .package.source import Archive, GitRepository

PKGS: List[Pkg] = [
    MesonPkg(Archive.gnome(name="glib", major=2, minor=75, patch=0)),
    MesonPkg(Archive.gnome(name="gtk", major=4, minor=8, patch=2)),
    MesonPkg(Archive.gnome(name="pygobject", major=3, minor=42, patch=0)),
    MesonPkg(GitRepository.github("wizbright", "waybox")),
    MesonPkg(GitRepository.github("labwc", "labwc")),
    MesonPkg(
        Archive.from_url(
            "https://gitlab.freedesktop.org/mesa/drm/-/archive/libdrm-2.4.114/drm-libdrm-2.4.114.tar.bz2"
        )
    ),
    # TODO: move prefix/share/pkgconfig/wayland-protocols.pc to lib64/pkgconfig
    MesonPkg(
        Archive.from_url(
            "https://gitlab.freedesktop.org/wayland/wayland-protocols/-/archive/1.29/wayland-protocols-1.29.tar.bz2"
        )
    ),
    MesonPkg(
        Archive.github_tag(
            "MusicPlayerDaemon", "MPD", "v0.23.10", archive_name="MPD-0.23.10.tar.gz"
        )
    ),
    MesonPkg(
        Archive.codeberg_tag(
            "dnkl",
            "foot",
            "1.13.1",
            archive_name="foot.tar.gz",
        )
    ),
    MesonPkg(
        Archive.from_url(
            "https://github.com/harfbuzz/harfbuzz/releases/download/5.3.1/harfbuzz-5.3.1.tar.xz"
        )
    ),
    MesonPkg(
        Archive.codeberg_tag("dnkl", "tllist", "1.1.0", archive_name="tllist.tar.gz")
    ),
    CMakePkg(
        Archive.from_url(
            "https://download.gnome.org/sources/libxml2/2.10/libxml2-2.10.3.tar.xz"
        )
    ),
]


def list_pkgs():
    for pkg in PKGS:
        print(pkg)


def get_pkg(name: str) -> Optional[Pkg]:
    for pkg in PKGS:
        if pkg.source.name == name:
            return pkg
