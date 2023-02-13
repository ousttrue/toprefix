from typing import Protocol, Optional, Tuple
import pathlib


class Source(Protocol):
    name: str

    def extract(self, src_dir: pathlib.Path) -> Optional[pathlib.Path]:
        ...
