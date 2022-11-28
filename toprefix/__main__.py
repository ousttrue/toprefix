from typing import Optional
import argparse
import logging
import os
import platform
import pathlib
from . import packages
from . import _version

LOGGER = logging.getLogger(__name__)
HOME = pathlib.Path(os.environ["HOME"])
PREFIX = HOME / "prefix"
PREFIX_SRC = HOME / "local/src"
EXE = ".exe" if platform.system() == "Windows" else ""


def unexpand(src: pathlib.Path) -> str:
    relative = []
    current = src
    while True:
        if current == HOME:
            relative.insert(0, "~")
            return "/".join(relative)
        if current.root == current:
            break

        relative.insert(0, current.name)
        current = current.parent

    return str(src)


def which(cmd: str) -> Optional[pathlib.Path]:
    for path in os.environ["PATH"].split(os.pathsep):
        fullpath = pathlib.Path(path) / cmd
        if fullpath.exists():
            return fullpath


def print_cmd(cmd: str):
    found = which(f"{cmd}{EXE}")
    if found:
        print(f"    {cmd}: {found}")
    else:
        print(f"    {cmd}: not found")


def main():
    parser = argparse.ArgumentParser(
        prog="toprefix", description="Build automation to prefix"
    )
    subparsers = parser.add_subparsers(dest="subparser_name")

    parser_version = subparsers.add_parser("version")

    parser_list = subparsers.add_parser("list")

    parser_build = subparsers.add_parser("install")
    parser_build.add_argument("package")
    parser_build.add_argument("--clean", action=argparse.BooleanOptionalAction)
    parser_build.add_argument("--reconfigure", action=argparse.BooleanOptionalAction)

    args = parser.parse_args()

    match args.subparser_name:
        case "version":
            print(_version.version)

        case "list":
            LOGGER.info("list")
            packages.list_pkgs()

        case "install":
            pkg = packages.get_pkg(args.package)
            assert pkg
            pkg.process(
                prefix=PREFIX,
                src=PREFIX_SRC,
                clean=args.clean,
                reconfigure=args.reconfigure,
            )

        case _:
            parser.print_help()
            print()
            print("environment:")
            print(f"    prefix: {unexpand(PREFIX)}")
            print(f"    src: {unexpand(PREFIX_SRC)}")
            print()
            print_cmd("pkg-config")
            # pkg_config status: PKG_CONFIG_PATH
            print_cmd("flex")
            print_cmd("bison")
            print_cmd("ninja")
            print_cmd("cmake")
            print_cmd("meson")
            print_cmd("make")
            print()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
