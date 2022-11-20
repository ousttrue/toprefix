#!/usr/bin/env python
import argparse
import pathlib
import os
import requests
import shutil
import logging
import subprocess
from tqdm import tqdm
from typing import NamedTuple

LOGGER = logging.getLogger(__name__)

PREFIX = pathlib.Path(os.environ["HOME"]) / "prefix"
PREFIX_SRC = PREFIX / "src"
GNOME_SOURCE_URL = "https://download.gnome.org/sources/{name}/{major}.{minor}/{name}-{major}.{minor}.{patch}.tar.xz"


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


def run(cmd: str, env: dict):
    subprocess.run(cmd, env=env, shell=True)


class MesonPkg(NamedTuple):
    name: str
    version: str
    url: str

    @staticmethod
    def from_gnome(name: str, major: int, minor: int, patch: int) -> "MesonPkg":
        return MesonPkg(
            name,
            f"{major}.{minor}.{patch}",
            GNOME_SOURCE_URL.format(name=name, major=major, minor=minor, patch=patch),
        )

    def __str__(self) -> str:
        return f"{self.name}-{self.version}"

    def get_download_dst(self, src: pathlib.Path) -> pathlib.Path:
        return src / os.path.basename(self.url)

    def get_extract_dst(self, src: pathlib.Path) -> pathlib.Path:
        basename = os.path.basename(self.url)
        if basename.endswith(".tar.xz"):
            return src / basename[0:-7]
        raise NotImplementedError(basename)

    def make_env(self) -> dict:
        env = {k: v for k, v in os.environ.items()}
        env["PKG_CONFIG_PATH"] = prefix / "lib/pkgconfig"

    def configure(self, source_dir: pathlib.Path, prefix: pathlib.Path):
        if (source_dir / 'build').exists():
            return
        cwd = os.getcwd()
        try:
            os.chdir(source_dir)
            run(f"meson setup build --prefix {prefix}", env=self.make_env())
        finally:
            os.chdir(cwd)

    def build(self, source_dir: pathlib.Path, prefix: pathlib.Path):
        cwd = os.getcwd()
        try:
            os.chdir(source_dir)
            run(f"meson compile -C build", env=self.make_env())
        finally:
            os.chdir(cwd)

    def install(self, source_dir: pathlib.Path, prefix: pathlib.Path):
        cwd = os.getcwd()
        try:
            os.chdir(source_dir)
            run(f"meson install -C build", env=self.make_env())
        finally:
            os.chdir(cwd)


PKGS = [MesonPkg.from_gnome("pygobject", 3, 42, 0)]


def list_pkgs():
    for pkg in PKGS:
        print(pkg)


def get_pkg(name: str):
    for pkg in PKGS:
        if pkg.name == name:
            return pkg


def process(pkg: MesonPkg):
    download = pkg.get_download_dst(PREFIX_SRC)
    if not download.exists():
        LOGGER.info(f"download: {download}")
        do_download(pkg.url, download)

    # extract
    extract = pkg.get_extract_dst(PREFIX_SRC)
    if not extract.exists():
        LOGGER.info(f"extract: {extract}")
        do_extract(download, extract)

    # patch
    # TODO: master => main

    # build
    pkg.configure(extract, PREFIX)
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

    args = parser.parse_args()

    match args.subparser_name:
        case "list":
            LOGGER.info("list")
            list_pkgs()

        case "install":
            pkg = get_pkg(args.package)
            LOGGER.info(f"install: {pkg}")
            process(pkg)

        case _:
            parser.print_help()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
