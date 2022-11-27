from typing import Protocol, Optional
import pathlib
import os
import re
import shutil
import logging
import requests
import tqdm
from . import pkg

LOGGER = logging.getLogger(__name__)

# archive
GITHUB_TAG_URL = "https://github.com/{user}/{name}/archive/refs/tags/{tag}.tar.gz"
CODEBERG_TAG_URL = "https://codeberg.org/{user}/{name}/archive/{tag}.tar.gz"
GNOME_SOURCE_URL = "https://download.gnome.org/sources/{name}/{major}.{minor}/{name}-{major}.{minor}.{patch}.tar.xz"

# git repository
GITHUB_URL = "https://github.com/{user}/{name}.git"
GITLAB_URL = "https://gitlab.freedesktop.org/{user}/{name}.git"


class Source(Protocol):
    name: str

    def extract(self, src_dir: pathlib.Path) -> Optional[pathlib.Path]:
        ...


class Archive(Source):
    def __init__(
        self, name: str, version: str, url: str, *, archive_name: Optional[str] = None
    ) -> None:
        self.name = name
        self.version = version
        self.url = url
        if not archive_name:
            archive_name = os.path.basename(self.url)
            assert archive_name
        self.archive_name = archive_name

    def __str__(self) -> str:
        return f"{self.name}-{self.version}"

    @staticmethod
    def from_url(url: str) -> "Archive":
        basename = os.path.basename(url)
        if basename.endswith(".tar.xz"):
            stem = basename[0:-7]
        elif basename.endswith(".tar.bz2"):
            stem = basename[0:-8]
        else:
            raise NotImplementedError(url)

        # expect
        # {stem}-{version}{extension}
        m = re.match(r"^(.*)-(\d+)\.(\d+)(\.\d+)?$", stem)
        if not m:
            raise NotImplementedError(stem)

        name = m.group(1)
        major = m.group(2)
        minor = m.group(3)
        patch = m.group(4)
        if not patch:
            patch = ""
        return Archive(
            name,
            f"{major}.{minor}{patch}",
            url,
        )

    @staticmethod
    def gnome(name: str, major, minor, patch) -> "Archive":
        return Archive.from_url(
            GNOME_SOURCE_URL.format(name=name, major=major, minor=minor, patch=patch)
        )

    @staticmethod
    def github_tag(user: str, name: str, tag: str, archive_name: str) -> "Archive":
        return Archive(
            name,
            tag,
            GITHUB_TAG_URL.format(user=user, name=name, tag=tag),
            archive_name=archive_name,
        )

    @staticmethod
    def codeberg_tag(user: str, name: str, tag: str, archive_name: str) -> "Archive":
        return Archive(
            name,
            tag,
            CODEBERG_TAG_URL.format(user=user, name=name, tag=tag),
            archive_name=archive_name,
        )

    def extract(self, src: pathlib.Path) -> Optional[pathlib.Path]:
        download = src / self.archive_name
        if not download.exists():
            LOGGER.info(f"download: {download}")
            self.do_download(self.url, download)

        extract = self.get_extract_dst(src)
        if not extract.exists():
            LOGGER.info(f"extract: {extract}")
            self.do_extract(download, extract)

        return extract

    def do_download(self, url: str, dst: pathlib.Path):
        try:
            size = int(requests.head(url).headers["content-length"])
        except KeyError:
            size = 0

        res = requests.get(url, stream=True)
        pbar = tqdm.tqdm(total=size, unit="B", unit_scale=True)

        dst.parent.mkdir(exist_ok=True, parents=True)
        with dst.open("wb") as file:
            for chunk in res.iter_content(chunk_size=1024):
                file.write(chunk)
                pbar.update(len(chunk))
            pbar.close()

    def do_extract(self, archive: pathlib.Path, dst: pathlib.Path):
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.unpack_archive(archive, dst.parent)

    def get_extract_dst(self, src: pathlib.Path) -> pathlib.Path:
        if self.archive_name.endswith(".tar.xz"):
            return src / self.archive_name[0:-7]
        elif self.archive_name.endswith(".tar.gz"):
            return src / self.archive_name[0:-7]
        elif self.archive_name.endswith(".tar.bz2"):
            return src / self.archive_name[0:-8]
        else:
            raise NotImplementedError(self.archive_name)


class GitRepository(Source):
    def __init__(self, name: str, url: str) -> None:
        self.name = name
        self.url = url

    def __str__(self) -> str:
        return f"{self.name}: {self.url}"

    @staticmethod
    def github(user: str, name: str) -> "GitRepository":
        return GitRepository(
            name,
            GITHUB_URL.format(user=user, name=name),
        )

    @staticmethod
    def from_gitlab(user: str, name: str) -> "GitRepository":
        return GitRepository(
            name,
            GITLAB_URL.format(user=user, name=name),
        )

    def do_clone(self, url: str, dst: pathlib.Path):
        dst.parent.mkdir(parents=True, exist_ok=True)
        with pkg.pushd(dst.parent):
            pkg.run(f"git clone {url}", None)

    def extract(self, src_dir: pathlib.Path):
        clone = src_dir / self.name
        if not clone.exists():
            LOGGER.info(f"clone: {clone}")
            self.do_clone(self.url, clone)
        return clone
