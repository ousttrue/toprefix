from typing import Optional
import argparse
import logging
import os
import sys
import platform
import pathlib
import toml
from . import packages
from . import _version

LOGGER = logging.getLogger(__name__)
HOME = pathlib.Path(os.environ["HOME"])
PREFIX = HOME / "prefix"
PREFIX_SRC = HOME / "local/src"
EXE = ".exe" if platform.system() == "Windows" else ""
CONFIG_TOML = HOME / ".config/toprefix/toprefix.toml"

if CONFIG_TOML.exists():
    config = toml.load(CONFIG_TOML)
    prefix = config.get("prefix")
    if prefix:
        PREFIX = pathlib.Path(prefix)


def unexpand(src: pathlib.Path) -> str:
    relative = []
    current = src
    while True:
        if current == HOME:
            relative.insert(0, "~")
            return "/".join(relative)
        if current.parent == current:
            break

        relative.insert(0, current.name)
        current = current.parent

    return str(src)


def which(cmd: str) -> Optional[pathlib.Path]:
    for path in os.environ["PATH"].split(os.pathsep):
        fullpath = pathlib.Path(path) / cmd
        if fullpath.exists():
            return fullpath


def print_cmd(*cmds: str):
    for cmd in cmds:
        found = which(f"{cmd}{EXE}")
        if found:
            print(f"    {cmd}: {found}")
            return
    print(f"    {cmds}: not found")


def has_env(key: str, path: pathlib.Path) -> bool:
    for x in os.environ.get(key, "").split(os.pathsep):
        if path == pathlib.Path(x):
            return True
    return False


def check_prefix_env_path(key: str, value: str, *, indent: str = "        "):
    print(
        f"{indent}ENV{{{key}}} has {{PREFIX}}/{value}: {has_env(key, PREFIX / value)}"
    )


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
            # TODO: color print
            # https://kaworu.jpn.org/kaworu/2018-05-19-1.php
            print()
            print("environment:")
            print(f"    PREFIX: {unexpand(PREFIX)}")
            # PATH
            check_prefix_env_path("PATH", "bin")
            # LD_LIBRARY_PATH
            if platform.system() != "Windows":
                check_prefix_env_path("LD_LIBRARY_PATH", "lib64")
            # PKG_CONFIG_PATH
            if platform.system() != "Windows":
                check_prefix_env_path("PKG_CONFIG_PATH", "lib64/pkgconfig")
                check_prefix_env_path("PKG_CONFIG_PATH", "share/pkgconfig")
            else:
                check_prefix_env_path("PKG_CONFIG_PATH", "lib/pkgconfig")
                check_prefix_env_path("PKG_CONFIG_PATH", "share/pkgconfig")
            # PYTHONPATH
            if platform.system() != "Windows":
                python_lib_path = (
                    PREFIX
                    / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site_packages"
                )
            else:
                python_lib_path = PREFIX / f"lib/site-packages"
            has_sys_path = any(
                x for x in sys.path if pathlib.Path(x) == python_lib_path
            )
            if has_sys_path:
                print(f"        sys.path has {python_lib_path}")
            else:
                print(sys.path)
                if platform.system() != "Windows":
                    check_prefix_env_path(
                        "PYTHONPATH",
                        f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages",
                    )
                else:
                    check_prefix_env_path(
                        "PYTHONPATH",
                        f"lib/site-packages",
                    )

            print(f"    SRC: {unexpand(PREFIX_SRC)}")
            print()
            print("tools:")
            print_cmd("pkg-config")
            # pkg_config status: PKG_CONFIG_PATH
            print_cmd("flex", "win_flex")
            print_cmd("bison", "win_bison")
            print_cmd("ninja")
            print_cmd("cmake")
            print_cmd("meson")
            print_cmd("make")
            print()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
