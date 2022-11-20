#!/usr/bin/env python
import argparse
import pathlib
import os
import requests
import shutil
import logging
import subprocess
from contextlib import contextmanager
import re
from tqdm import tqdm
from typing import NamedTuple

LOGGER = logging.getLogger(__name__)

HOME = pathlib.Path(os.environ["HOME"])
PREFIX = HOME / "prefix"
PREFIX_SRC = HOME / "prefix_work/src"
GNOME_SOURCE_URL = "https://download.gnome.org/sources/{name}/{major}.{minor}/{name}-{major}.{minor}.{patch}.tar.xz"
GITHUB_URL = "https://github.com/{user}/{name}.git"
GITLAB_URL = "https://gitlab.freedesktop.org/{user}/{name}.git"


def gnome_url(name: str, major: int, minor: int, patch: int) -> str:
    return GNOME_SOURCE_URL.format(name=name, major=major, minor=minor, patch=patch)


def run(cmd: str, env: dict):
    LOGGER.debug(cmd)
    subprocess.run(cmd, env=env, shell=True, check=True)


def do_download(url: str, dst: pathlib.Path):
    try:
        size = int(requests.head(url).headers["content-length"])
    except KeyError:
        size = 0

    res = requests.get(url, stream=True)
    pbar = tqdm(total=size, unit="B", unit_scale=True)

    dst.parent.mkdir(exist_ok=True, parents=True)
    with dst.open("wb") as file:
        for chunk in res.iter_content(chunk_size=1024):
            file.write(chunk)
            pbar.update(len(chunk))
        pbar.close()


def do_extract(archive: pathlib.Path, dst: pathlib.Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.unpack_archive(archive, dst.parent)


def do_clone(url: str, dst: pathlib.Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    with pushd(dst.parent):
        run(f"git clone {url}", {})


def make_env(prefix: pathlib.Path) -> dict:
    env = {k: v for k, v in os.environ.items()}
    env["PKG_CONFIG_PATH"] = prefix / "lib64/pkgconfig"
    return env


@contextmanager
def pushd(path: pathlib.Path):
    LOGGER.debug(f"pushd: {path}")
    cwd = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        LOGGER.debug(f"popd: {cwd}")
        os.chdir(cwd)


class MesonPkg(NamedTuple):
    name: str
    version: str
    url: str

    @staticmethod
    def from_url(url: str) -> "MesonPkg":
        basename = os.path.basename(url)
        if basename.endswith(".tar.xz"):
            stem = basename[0:-7]
        elif basename.endswith(".tar.bz2"):
            stem = basename[0:-8]
        # expect
        # {stem}-{version}{extension}
        m = re.match(r"^(.*)-(\d+)\.(\d+)(\.\d+)?$", stem)
        if m:
            name = m.group(1)
            major = m.group(2)
            minor = m.group(3)
            patch = m.group(4)
            if not patch:
                patch = ""
        else:
            print(stem)

        return MesonPkg(
            name,
            f"{major}.{minor}{patch}",
            url,
        )

    @staticmethod
    def from_github(user: str, name: str) -> "MesonPkg":
        return MesonPkg(
            name,
            "git",
            GITHUB_URL.format(user=user, name=name),
        )

    @staticmethod
    def from_gitlab(user: str, name: str) -> "MesonPkg":
        return MesonPkg(
            name,
            "git",
            GITLAB_URL.format(user=user, name=name),
        )

    def __str__(self) -> str:
        return f"{self.name}-{self.version}"

    def get_download_dst(self, src: pathlib.Path) -> pathlib.Path:
        if self.version != "git":
            return src / os.path.basename(self.url)

    def get_clone_dst(self, src: pathlib.Path) -> pathlib.Path:
        if self.version == "git":
            return src / self.name

    def get_extract_dst(self, src: pathlib.Path) -> pathlib.Path:
        basename = os.path.basename(self.url)
        if basename.endswith(".tar.xz"):
            return src / basename[0:-7]
        elif basename.endswith(".tar.bz2"):
            return src / basename[0:-8]
        else:
            raise NotImplementedError(basename)

    def configure(
        self,
        source_dir: pathlib.Path,
        prefix: pathlib.Path,
        *,
        clean: bool,
        reconfigure: bool,
    ):
        LOGGER.info(f"configure: {source_dir} => {prefix}")
        with pushd(source_dir):
            if not (source_dir / "build").exists():
                run(f"meson setup build --prefix {prefix}", env=make_env(prefix))
            else:
                if clean:
                    shutil.rmtree(source_dir / "build")
                    run(f"meson setup build --prefix {prefix}", env=make_env(prefix))
                elif reconfigure:
                    run(
                        f"meson setup build --prefix {prefix} --reconfigure",
                        env=make_env(prefix),
                    )

    def build(self, source_dir: pathlib.Path, prefix: pathlib.Path):
        LOGGER.info(f"build: {source_dir} => {prefix}")
        with pushd(source_dir):
            run(f"meson compile -C build", env=make_env(prefix))

    def install(self, source_dir: pathlib.Path, prefix: pathlib.Path):
        LOGGER.info(f"install: {source_dir} => {prefix}")
        with pushd(source_dir):
            run(f"meson install -C build", env=make_env(prefix))


PKGS = [
    MesonPkg.from_url(gnome_url("glib", 2, 75, 0)),
    MesonPkg.from_url(gnome_url("gtk", 4, 8, 2)),
    MesonPkg.from_url(gnome_url("pygobject", 3, 42, 0)),
    MesonPkg.from_github("wizbright", "waybox"),
    MesonPkg.from_github("labwc", "labwc"),
    MesonPkg.from_url(
        "https://gitlab.freedesktop.org/mesa/drm/-/archive/libdrm-2.4.114/drm-libdrm-2.4.114.tar.bz2"
    ),
    # TODO: move prefix/share/pkgconfig/wayland-protocols.pc to lib64/pkgconfig
    MesonPkg.from_url(
        "https://gitlab.freedesktop.org/wayland/wayland-protocols/-/archive/1.29/wayland-protocols-1.29.tar.bz2"
    ),
]


def list_pkgs():
    for pkg in PKGS:
        print(pkg)


def get_pkg(name: str):
    for pkg in PKGS:
        if pkg.name == name:
            return pkg


def process(pkg: MesonPkg, *, clean: bool, reconfigure: bool):
    download = pkg.get_download_dst(PREFIX_SRC)
    if download:
        if not download.exists():
            LOGGER.info(f"download: {download}")
            do_download(pkg.url, download)

        # extract
        extract = pkg.get_extract_dst(PREFIX_SRC)
        if not extract.exists():
            LOGGER.info(f"extract: {extract}")
            do_extract(download, extract)

    clone = pkg.get_clone_dst(PREFIX_SRC)
    if clone:
        if not clone.exists():
            LOGGER.info(f"clone: {clone}")
            do_clone(pkg.url, clone)
        extract = clone

    # patch
    # TODO: master => main

    # build
    pkg.configure(extract, PREFIX, clean=clean, reconfigure=reconfigure)
    pkg.build(extract, PREFIX)
    pkg.install(extract, PREFIX)


def main():
    parser = argparse.ArgumentParser(
        prog="toprefix", description="Build automation to prefix"
    )
    subparsers = parser.add_subparsers(dest="subparser_name")

    parser_list = subparsers.add_parser("list")

    parser_build = subparsers.add_parser("install")
    parser_build.add_argument("package")
    parser_build.add_argument("--clean", action=argparse.BooleanOptionalAction)
    parser_build.add_argument("--reconfigure", action=argparse.BooleanOptionalAction)

    args = parser.parse_args()

    match args.subparser_name:
        case "list":
            LOGGER.info("list")
            list_pkgs()

        case "install":
            pkg = get_pkg(args.package)
            LOGGER.info(f"install: {pkg}")
            process(pkg, clean=args.clean, reconfigure=args.reconfigure)

        case _:
            parser.print_help()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
