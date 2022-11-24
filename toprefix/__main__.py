import argparse
import logging
import os
import pathlib
from .packages import MesonPkg, PKGS

LOGGER = logging.getLogger(__name__)
HOME = pathlib.Path(os.environ["HOME"])
PREFIX = HOME / "prefix"
PREFIX_SRC = HOME / "prefix_work/src"


def list_pkgs():
    for pkg in PKGS:
        print(pkg)


def get_pkg(name: str):
    for pkg in PKGS:
        if pkg.name == name:
            return pkg


def process(pkg: MesonPkg, *, clean: bool, reconfigure: bool):
    extract = pkg.download_extract_or_clone(PREFIX_SRC)
    assert extract

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
            assert pkg
            LOGGER.info(f"install: {pkg}")
            process(pkg, clean=args.clean, reconfigure=args.reconfigure)

        case _:
            parser.print_help()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
