from typing import Tuple, Optional
import os
import logging
import pathlib
import requests
import shutil
import re
import tqdm
import tempfile
from .source import Source
from toprefix import util


def archive_ext(src: str) -> Tuple[str, str]:
    if src.endswith(".tar.xz"):
        return src[0:-7], ".tar.xz"
    elif src.endswith(".tar.gz"):
        return src[0:-7], ".tar.gz"
    elif src.endswith(".tar.bz2"):
        return src[0:-8], ".tar.bz2"
    elif src.endswith(".zip"):
        return src[0:-4], ".zip"
    else:
        raise NotImplementedError(src)


LOGGER = logging.getLogger(__name__)

# archive
GITHUB_TAG_URL = "https://github.com/{user}/{name}/archive/refs/tags/{tag}.tar.gz"
CODEBERG_TAG_URL = "https://codeberg.org/{user}/{name}/archive/{tag}.tar.gz"
SOURCEHUT_TAG_URL = "https://git.sr.ht/~{user}/{name}/archive/{tag}.tar.gz"
GNOME_SOURCE_URL = "https://download.gnome.org/sources/{name}/{major}.{minor}/{name}-{major}.{minor}.{patch}.tar.xz"


VERSION_PATTERN = re.compile(r"^(\d+)\.(\d+)(?:\.(\d+))?$")


class Archive(Source):
    def __init__(
        self, name: str, version: str, url: str, archive_name: Optional[str] = None
    ) -> None:
        self.name = name
        self.version = version
        self.url = url
        if not archive_name:
            archive_name = os.path.basename(self.url)
        self.archive_name = archive_name

    def __str__(self) -> str:
        return f"{self.name}-{self.version}"

    @staticmethod
    def from_url(url: str) -> "Archive":
        basename = os.path.basename(url)
        stem, _ = archive_ext(basename)

        # {stem}-{version}{extension}
        m = re.match(r"^(.*)-(\d+)\.(\d+)(\.\d+)?$", stem)
        if m:
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

        # go1.19.3.linux-amd64.tar.gz
        m = re.match(r"^(.*)(\d+)\.(\d+)(\.\d+)\.linux-amd64$", stem)
        if m:
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

        # releases/download/v1.3.0/ghq_linux_amd64.zip
        m = re.search(r"/releases/download/([^/]+)/ghq_linux_amd64\.zip$", url)
        if m:
            name = "ghq"
            version = m.group(1)
            return Archive(
                name,
                version,
                url,
            )

        # releases/download/llvmorg-15.0.6/llvm-15.0.6.src.tar.xz
        m = re.search(
            r"/releases/download/[^/]+/llvm-project-(\d+\.\d+\.\d+)\.src\.tar\.xz$", url
        )
        if m:
            name = "llvm"
            version = m.group(1)
            return Archive(
                name,
                version,
                url,
            )

        raise NotImplementedError(stem)

    @staticmethod
    def gnome(name: str, version: str) -> "Archive":
        m = VERSION_PATTERN.match(version)
        assert m
        return Archive.from_url(
            GNOME_SOURCE_URL.format(
                name=name,
                major=m.group(1),
                minor=m.group(2),
                patch=m.group(3),
            )
        )

    @staticmethod
    def github_tag(user: str, name: str, tag: str) -> "Archive":
        return Archive(
            name,
            tag,
            GITHUB_TAG_URL.format(user=user, name=name, tag=tag),
            f"{name}-{tag}.tar.gz",
        )

    @staticmethod
    def github_head(user: str, name: str) -> "Archive":
        return Archive(
            name,
            "head",
            f"https://github.com/{user}/{name}/archive/refs/heads/master.zip",
            f"{name}.zip",
        )

    @staticmethod
    def codeberg_tag(user: str, name: str, tag: str) -> "Archive":
        return Archive(
            name,
            tag,
            CODEBERG_TAG_URL.format(user=user, name=name, tag=tag),
            archive_name=f"{name}-{tag}.tar.gz",
        )

    @staticmethod
    def sourcehut_tag(user: str, name: str, tag: str) -> "Archive":
        return Archive(
            name,
            tag,
            SOURCEHUT_TAG_URL.format(user=user, name=name, tag=tag),
            archive_name=f"{name}-{tag}.tar.gz",
        )

    def extract(self, src: pathlib.Path) -> Optional[pathlib.Path]:
        download = src / self.archive_name
        if download.exists():
            LOGGER.info(f"exists: {download}")
        else:
            LOGGER.info(f"download: {download}")
            self.do_download(self.url, download)

        stem, _ = archive_ext(self.archive_name)
        extract = src / stem
        if not extract.exists():
            with tempfile.TemporaryDirectory() as dname:
                dst = pathlib.Path(dname)
                with util.pushd(dst):
                    shutil.unpack_archive(download)

                    # check result
                    items = [f for f in dst.iterdir()]
                    if len(items) != 1:
                        raise Exception(f"extrac many root: {items}")

                    # move to dst
                    shutil.move(items[0], extract)

            print(os.path.exists(dname))  # False

            # LOGGER.info(f"extract: {extract}")
            # self.do_extract(download, extract)

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
