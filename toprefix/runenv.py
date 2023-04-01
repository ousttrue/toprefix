from typing import Optional, List
import pathlib, os, platform, sys
import toml
import logging
import contextlib
import subprocess
from colorama import Fore
from . import vcenv

IS_WINDOWS = platform.system() == "Windows"

LOGGER = logging.getLogger(__name__)

HOME = pathlib.Path(os.environ["USERPROFILE"] if IS_WINDOWS else os.environ["HOME"])
PREFIX = HOME / "prefix"
LOCAL_BIN = HOME / "local/bin"
LOCAL_SRC = HOME / "local/src"
EXE = ".exe" if IS_WINDOWS else ""

CONFIG_TOML = HOME / ".config/toprefix/toprefix.toml"
if CONFIG_TOML.exists():
    config = toml.load(CONFIG_TOML)
    prefix = config.get("prefix")
    if prefix:
        PREFIX = pathlib.Path(prefix)

PATH_LIST = os.environ["PATH"].split(os.pathsep)


def minimum_env():
    git = which("git")
    if not git:
        raise Exception("git required")
    env = {}
    path: List[str] = [
        str(git.parent),
    ]
    if IS_WINDOWS:
        path.append(os.environ["SystemRoot"] + "\\System32")
        path.append(os.environ["SystemRoot"] + "\\System32\\WindowsPowerShell\\v1.0")
        for k in (
            "SystemRoot",
            "APPDATA",
            "LOCALAPPDATA",
            "ComSpec",
            "OS",
            "NUMBER_OF_PROCESSORS",
            "PROCESSOR_ARCHITECTURE",
            "PROCESSOR_IDENTIFIER",
            "PROCESSOR_LEVEL",
            "PROCESSOR_REVISION",
            "POWERSHELL_DISTRIBUTION_CHANNEL",
            "PSModulePath",
            "TEMP",
            "TMP",
            "USERNAME",
            "USERPROFILE",
        ):
            env[k] = os.environ[k]
        env["PATH"] = ";".join(path)
    else:
        path.append("/bin")
        path.append("/usr/bin")
        path.append("/sbin")
        env["PATH"] = ":".join(path)
        for k in (
            "HOME",
            "LANG",
            "USER",
            "SHELL",
            # "HOSTTYPE",
        ):
            env[k] = os.environ[k]

    return env


def unexpand(src: pathlib.Path) -> str:
    relative = []
    current = src
    while True:
        if current == HOME:
            relative.insert(0, "~")
            return "/".join(relative)
        if current.parent == current:
            break

        relative.insert(0, current.name)
        current = current.parent

    return str(src)


def which(cmd: str) -> Optional[pathlib.Path]:
    for path in PATH_LIST:
        fullpath = pathlib.Path(path) / f"{cmd}{EXE}"
        if fullpath.exists():
            return fullpath


def print_cmd(*cmds: str):
    for cmd in cmds:
        found = which(f"{cmd}")
        if found:
            print(f"    {cmds[0]}: {Fore.GREEN}{found}{Fore.RESET}")
            return
    print(f"    {cmds[0]}: {Fore.RED}not found{Fore.RESET}")


def has_env(key: str, path: pathlib.Path) -> bool:
    for x in os.environ.get(key, "").split(os.pathsep):
        if path == pathlib.Path(x):
            return True
    return False


def check_prefix_env_path(key: str, value: str, *, indent: str = "        "):
    has = has_env(key, PREFIX / value)
    if has:
        print(
            f"{indent}ENV{{{key}}} has {{PREFIX}}/{value}: {Fore.GREEN}True{Fore.RESET}"
        )
    else:
        print(
            f"{indent}ENV{{{key}}} has {{PREFIX}}/{value}: {Fore.RED}False{Fore.RESET}"
        )


def run(cmd: str, *, check=True):
    env = minimum_env()
    env.update(vcenv.get_env(env))
    cmd = cmd.format(PREFIX=PREFIX)
    LOGGER.debug(cmd)
    LOGGER.debug(env.keys())
    subprocess.run(cmd, env=env, shell=True, check=check)


# def make_env(prefix: pathlib.Path) -> dict:
#     return None
#     # env = {k: v for k, v in os.environ.items()}
#     # env["PKG_CONFIG_PATH"] = str(prefix / "lib64/pkgconfig")
#     # return env


def print_env():
    # TODO: color print
    # https://kaworu.jpn.org/kaworu/2018-05-19-1.php
    print()
    print("environment:")
    print(f"  TOOLS: {Fore.CYAN}{unexpand(LOCAL_BIN)}{Fore.RESET}")
    print(f"  PREFIX: {Fore.CYAN}{unexpand(PREFIX)}{Fore.RESET}")
    # PATH
    check_prefix_env_path("PATH", "bin")
    # LD_LIBRARY_PATH
    if not IS_WINDOWS:
        check_prefix_env_path("LD_LIBRARY_PATH", "lib64")
    # PKG_CONFIG_PATH
    if not IS_WINDOWS:
        check_prefix_env_path("PKG_CONFIG_PATH", "lib64/pkgconfig")
        check_prefix_env_path("PKG_CONFIG_PATH", "share/pkgconfig")
    else:
        check_prefix_env_path("PKG_CONFIG_PATH", "lib/pkgconfig")
        check_prefix_env_path("PKG_CONFIG_PATH", "share/pkgconfig")
    # PYTHONPATH
    if not IS_WINDOWS:
        python_lib_path = (
            PREFIX
            / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site_packages"
        )
    else:
        python_lib_path = PREFIX / f"lib/site-packages"
    has_sys_path = any(x for x in sys.path if pathlib.Path(x) == python_lib_path)
    if has_sys_path:
        print(f"    {Fore.GREEN}sys.path has {python_lib_path}{Fore.RESET}")
    else:
        # print(sys.path)
        if not IS_WINDOWS:
            check_prefix_env_path(
                "PYTHONPATH",
                f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages",
            )
        else:
            check_prefix_env_path(
                "PYTHONPATH",
                f"lib/site-packages",
            )

    print(f"  SRC: {Fore.CYAN}{unexpand(LOCAL_SRC)}{Fore.RESET}")
    print()

    if IS_WINDOWS:
        print(f"vcenv: {Fore.CYAN}{vcenv.get_vcbars()}{Fore.RESET}")
        env = minimum_env()
        for k, v in vcenv.get_env(env).items():
            print(f"  {k} =>")
            if k == "PATH":
                current = os.environ["PATH"].split(";")
                for vc_split in v.split(";"):
                    if vc_split not in current:
                        print(f"    {vc_split}")
            else:
                path_list = v.split(";")
                path_list.sort()
                for path in path_list:
                    print(f"    {path}")
        print()

    print("tools:")
    print_cmd("pkg-config")
    # pkg_config status: PKG_CONFIG_PATH
    print_cmd("flex", "win_flex")
    print_cmd("bison", "win_bison")
    print_cmd("ninja")
    print_cmd("cmake")
    print_cmd("meson")
    print_cmd("make")
    print_cmd("m4")
    print_cmd("perl")
    print()


def do_patch(dst: pathlib.Path, patches: List[pathlib.Path]):
    for patch in patches:
        LOGGER.info(f"apply: {patch}")
        with pushd(dst):
            run(f"patch -p0 < {patch}", check=False)


@contextlib.contextmanager
def pushd(path: pathlib.Path):
    LOGGER.debug(f"pushd: {path}")
    cwd = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        LOGGER.debug(f"popd: {cwd}")
        os.chdir(cwd)
