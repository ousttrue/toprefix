from typing import Protocol, Optional, Tuple, List
import pathlib
import re

# archive
GITHUB_TAG_URL = "https://github.com/{user}/{name}/archive/refs/tags/{tag}.tar.gz"
CODEBERG_TAG_URL = "https://codeberg.org/{user}/{name}/archive/{tag}.tar.gz"
SOURCEHUT_TAG_URL = "https://git.sr.ht/~{user}/{name}/archive/{tag}.tar.gz"
GNOME_SOURCE_URL = "https://download.gnome.org/sources/{name}/{major}.{minor}/{name}-{major}.{minor}.{patch}.tar.xz"

# git repository
GITHUB_URL = "https://github.com/{user}/{name}.git"
GITLAB_URL = "https://gitlab.freedesktop.org/{user}/{name}.git"

VERSION_PATTERN = re.compile(r"^(\d+)\.(\d+)(?:\.(\d+))?$")


class Source(Protocol):
    name: str
    patches: List[pathlib.Path] = []

    def extract(self, src_dir: pathlib.Path) -> Optional[pathlib.Path]:
        ...
