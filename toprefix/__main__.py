import argparse
import sys
import logging
import os
import pathlib
from . import packages
from . import _version

LOGGER = logging.getLogger(__name__)
HOME = pathlib.Path(os.environ["HOME"])
PREFIX = HOME / "prefix"
PREFIX_SRC = HOME / "local/src"


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
            # TODO:
            # PREFIX
            # PREFIX_SRC
            # pkg_config status: PKG_CONFIG_PATH
            # win_flex
            # win_byson
            # cmake status:
            # ninja status:
            parser.print_help()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
