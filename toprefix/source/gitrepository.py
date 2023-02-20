from .source import Source
import logging
import pathlib
from .. import runenv

LOGGER = logging.getLogger(__name__)

# git repository
GITHUB_URL = "https://github.com/{user}/{name}.git"
GITLAB_URL = "https://gitlab.freedesktop.org/{user}/{name}.git"


class GitRepository(Source):
    def __init__(self, name: str, url: str) -> None:
        self.name = name
        self.url = url
        self.patches = []

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
        with runenv.pushd(dst.parent):
            runenv.run(f"git clone {url}")

    def extract(self):
        clone = runenv.PREFIX_SRC / self.name
        if not clone.exists():
            LOGGER.info(f"clone: {clone}")
            self.do_clone(self.url, clone)

        runenv.do_patch(clone, self.patches)

        return clone
