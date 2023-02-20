import argparse
import logging
from . import package
from . import _version
from .envman import EnvMan
import colorama
from colorama import Fore

LOGGER = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.DEBUG)
    # handler = colorlog.StreamHandler()
    # handler.setFormatter(colorlog.ColoredFormatter(
    #     '%(log_color)s%(levelname)s:%(name)s:%(message)s'))
    # logging.root.handlers=[handler]
    colorama.init(autoreset=True)

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
            package.list_pkgs()

        case "install":
            pkg = package.get_pkg(args.package)
            if not pkg:
                print(f"{args.package} {Fore.RED}not found{Fore.RESET}")
                return
            pkg.process(
                env=EnvMan(),
                clean=args.clean,
                reconfigure=args.reconfigure,
            )

        case _:
            parser.print_help()
            env = EnvMan()
            env.print()


if __name__ == "__main__":
    main()
