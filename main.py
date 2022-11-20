#!/usr/bin/env python
import argparse
import pathlib
import os
import requests
from tqdm import tqdm
from typing import NamedTuple


PREFIX = pathlib.Path(os.environ['HOME']) / 'prefix'
PREFIX_SRC = PREFIX / 'src'
GNOME_SOURCE_URL = 'https://download.gnome.org/sources/{name}/{major}.{minor}/{name}-{major}.{minor}.{patch}.tar.xz'


def download(url: str, dst: pathlib.Path):
	try:
		size = int(requests.head(url).headers["content-length"])
	except KeyError:
		size = 0

	res = requests.get(url, stream=True)
	pbar = tqdm(total=size, unit="B", unit_scale=True)

	dst.parent.mkdir(exist_ok=True, parents=True)
	with dst.open('wb') as file:
		for chunk in res.iter_content(chunk_size=1024):
			file.write(chunk)
			pbar.update(len(chunk))
		pbar.close()


class MesonPkg(NamedTuple):
    name: str
    version: str
    url: str

    @staticmethod
    def from_gnome(name: str, major: int, minor: int, patch: int)->'MesonPkg':
        return MesonPkg(name, f'{major}.{minor}.{patch}', GNOME_SOURCE_URL.format(name=name, major=major, minor=minor, patch=patch))


PKGS = [ 
        MesonPkg.from_gnome('pygobject', 3, 42, 0)
        ]


def list_pkgs():
    for pkg in PKGS:
        print(pkg)

def get_pkg(name: str):
    for pkg in PKGS:
        if pkg.name == name:
            return pkg

def process(pkg: MesonPkg):
	dst = PREFIX_SRC / os.path.basename(pkg.url)
	if not dst.exists():
		# download
		download(pkg.url, dst)

    # extract

    # patch

    # build

    # install

def main():
    parser = argparse.ArgumentParser(
            prog = 'toprefix',
            description = 'Build automation to prefix'
            )
    subparsers = parser.add_subparsers(dest='subparser_name')

    parser_list = subparsers.add_parser('list')

    parser_build = subparsers.add_parser('install')
    parser_build.add_argument('package')

    args = parser.parse_args()

    match args.subparser_name:
        case 'list':
            list_pkgs()

        case 'install':
            pkg = get_pkg(args.package)
            process(pkg)

        case _:
            parser.print_help()


if __name__ == '__main__':
    main()

