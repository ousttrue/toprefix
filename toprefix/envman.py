from typing import Optional, Dict
import pathlib, os, platform, sys
import toml
import logging
import subprocess
import colorama
from colorama import Fore, Back, Style
from . import vcenv

LOGGER = logging.getLogger(__name__)


def minimum_env():
    env = {}
    path = [
        os.environ["SystemRoot"] + "\\System32",
        os.environ["SystemRoot"] + "\\System32\\WindowsPowerShell\\v1.0",
    ]
    env["PATH"] = ";".join(path)
    env["SystemRoot"] = os.environ["SystemRoot"]
    return env


class EnvMan:
    """
    環境変数管理
    """

    def __init__(self) -> None:
        self.HOME = pathlib.Path(os.environ["HOME"])
        self.PREFIX = self.HOME / "prefix"
        self.PREFIX_SRC = self.HOME / "local/src"
        self.EXE = ".exe" if platform.system() == "Windows" else ""

        self.CONFIG_TOML = self.HOME / ".config/toprefix/toprefix.toml"
        if self.CONFIG_TOML.exists():
            config = toml.load(self.CONFIG_TOML)
            prefix = config.get("prefix")
            if prefix:
                self.PREFIX = pathlib.Path(prefix)

        self.PATH_LIST = os.environ["PATH"].split(os.pathsep)

    def unexpand(self, src: pathlib.Path) -> str:
        relative = []
        current = src
        while True:
            if current == self.HOME:
                relative.insert(0, "~")
                return "/".join(relative)
            if current.parent == current:
                break

            relative.insert(0, current.name)
            current = current.parent

        return str(src)

    def which(self, cmd: str) -> Optional[pathlib.Path]:
        for path in self.PATH_LIST:
            fullpath = pathlib.Path(path) / cmd
            if fullpath.exists():
                return fullpath

    def print_cmd(self, *cmds: str):
        for cmd in cmds:
            found = self.which(f"{cmd}{self.EXE}")
            if found:
                print(f"    {cmds[0]}: {Fore.GREEN}{found}{Fore.RESET}")
                return
        print(f"    {cmds[0]}: {Fore.RED}not found{Fore.RESET}")

    def has_env(self, key: str, path: pathlib.Path) -> bool:
        for x in os.environ.get(key, "").split(os.pathsep):
            if path == pathlib.Path(x):
                return True
        return False

    def check_prefix_env_path(self, key: str, value: str, *, indent: str = "        "):
        has = self.has_env(key, self.PREFIX / value)
        if has:
            print(
                f"{indent}ENV{{{key}}} has {{PREFIX}}/{value}: {Fore.GREEN}True{Fore.RESET}"
            )
        else:
            print(
                f"{indent}ENV{{{key}}} has {{PREFIX}}/{value}: {Fore.RED}False{Fore.RESET}"
            )

    def apply_vcenv(self):
        for k, v in vcenv.get_env().items():
            if k == "PATH":
                current = os.environ["PATH"].split(";")
                add_path = [x for x in v.split(";") if x not in current]
                os.environ["PATH"] = ";".join(add_path) + ";" + os.environ["PATH"]
            else:
                os.environ[k] = v

    def run(self, cmd: str):
        env = minimum_env()
        for k in (
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

        env.update(vcenv.get_env(env))
        LOGGER.debug(cmd)
        LOGGER.debug(env.keys())
        subprocess.run(cmd.format(PREFIX=self.PREFIX), env=env, shell=True, check=True)

    # def make_env(prefix: pathlib.Path) -> dict:
    #     return None
    #     # env = {k: v for k, v in os.environ.items()}
    #     # env["PKG_CONFIG_PATH"] = str(prefix / "lib64/pkgconfig")
    #     # return env

    def print(self):
        # TODO: color print
        # https://kaworu.jpn.org/kaworu/2018-05-19-1.php
        print()
        print("environment:")
        print(f"  PREFIX: {Fore.CYAN}{self.unexpand(self.PREFIX)}{Fore.RESET}")
        # PATH
        self.check_prefix_env_path("PATH", "bin")
        # LD_LIBRARY_PATH
        if platform.system() != "Windows":
            self.check_prefix_env_path("LD_LIBRARY_PATH", "lib64")
        # PKG_CONFIG_PATH
        if platform.system() != "Windows":
            self.check_prefix_env_path("PKG_CONFIG_PATH", "lib64/pkgconfig")
            self.check_prefix_env_path("PKG_CONFIG_PATH", "share/pkgconfig")
        else:
            self.check_prefix_env_path("PKG_CONFIG_PATH", "lib/pkgconfig")
            self.check_prefix_env_path("PKG_CONFIG_PATH", "share/pkgconfig")
        # PYTHONPATH
        if platform.system() != "Windows":
            python_lib_path = (
                self.PREFIX
                / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site_packages"
            )
        else:
            python_lib_path = self.PREFIX / f"lib/site-packages"
        has_sys_path = any(x for x in sys.path if pathlib.Path(x) == python_lib_path)
        if has_sys_path:
            print(f"    {Fore.GREEN}sys.path has {python_lib_path}{Fore.RESET}")
        else:
            # print(sys.path)
            if platform.system() != "Windows":
                self.check_prefix_env_path(
                    "PYTHONPATH",
                    f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages",
                )
            else:
                self.check_prefix_env_path(
                    "PYTHONPATH",
                    f"lib/site-packages",
                )

        print(f"  SRC: {Fore.CYAN}{self.unexpand(self.PREFIX_SRC)}{Fore.RESET}")
        print()

        if platform.system() == "Windows":
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
        self.print_cmd("pkg-config")
        # pkg_config status: PKG_CONFIG_PATH
        self.print_cmd("flex", "win_flex")
        self.print_cmd("bison", "win_bison")
        self.print_cmd("ninja")
        self.print_cmd("cmake")
        self.print_cmd("meson")
        self.print_cmd("make")
        self.print_cmd("m4")
        self.print_cmd("perl")
        print()
