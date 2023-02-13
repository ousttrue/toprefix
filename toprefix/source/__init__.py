from .source import Source
from .archive import Archive
from .gitrepository import GitRepository

__all__ = ["Source", "Archive", "GitRepository"]


def get_source(name: str, item: dict) -> Source:
    match item["source"]:
        case {"gnome": gnome}:
            return Archive.gnome(name, gnome["version"])
        case {"url": url}:
            return Archive.from_url(url)
        case {"github": repo}:
            match repo:
                case {"user": user, "tag": tag}:
                    return Archive.github_tag(user, name, tag)
                case {"user": user}:
                    return Archive.github_head(user, name)
                case _:
                    raise NotImplementedError()
        case {"codeberg": repo}:
            if "tag" in repo:
                return Archive.codeberg_tag(repo["user"], name, repo["tag"])
            else:
                return GitRepository.github(repo["user"], name)
        case {"sourcehut": repo}:
            if "tag" in repo:
                return Archive.sourcehut_tag(repo["user"], name, repo["tag"])
            else:
                raise NotImplementedError()
        case _:
            raise NotImplementedError()
