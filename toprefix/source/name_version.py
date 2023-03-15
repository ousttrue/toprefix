from typing import Optional, Tuple
import re

TRIPLETS = [
    ".linux-amd64",
    "-windows-x86_64",
]

PATTERN = re.compile(r"^(.*)-?v?(\d+)(\.\d+)(\.\d+)?$")


def get_name_version(stem: str) -> Optional[Tuple[str, str]]:

    # some-v1.23.456
    # hoge-123.45.6
    # hoge-v1.23
    # hoge-1.23
    m = PATTERN.match(stem)
    if m:
        name = m.group(1)
        major = m.group(2)
        minor = m.group(3)
        patch = m.group(4)
        if not patch:
            patch = ""
        return (name, f"{major}{minor}{patch}")

    for triplet in TRIPLETS:
        if stem.endswith(triplet):
            m = PATTERN.match(stem[0 : -len(triplet)])
            if m:
                # go1.19.3.linux-amd64.tar.gz
                name = m.group(1)
                major = m.group(2)
                minor = m.group(3)
                patch = m.group(4)
                if not patch:
                    patch = ""
                return (name, f"{major}{minor}{patch}")
