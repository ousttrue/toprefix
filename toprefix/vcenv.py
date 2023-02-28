from typing import Dict, Optional
import platform
import os
import subprocess
import pathlib
import json
import vswhere



# VCBARS64_2019 = 'C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\BuildTools\\VC\\Auxiliary\\Build\\vcvars64.bat'
# VCBARS64_2022 = "C:\\Program Files (x86)\\Microsoft Visual Studio\\2022\\BuildTools\\VC\\Auxiliary\\Build\\vcvars64.bat"


def select_x64_kit() -> Optional[dict]:
    KITS = pathlib.Path(f"{os.environ['LOCALAPPDATA']}/CMakeTools/cmake-tools-kits.json")
    if KITS.exists():
        parsed = json.loads(KITS.read_text(encoding="utf-8"))
        for kit in parsed:
            match kit:
                case {
                    "preferredGenerator": {
                        "platform": "x64",
                        "toolset": "host=x64",
                    }
                }:
                    return kit


def get_vs_path(name: str) -> Optional[pathlib.Path]:
    for product in vswhere.find(products="*"):
        if product["displayName"] == name:
            return pathlib.Path(product["installationPath"])


def get_vcbars() -> pathlib.Path:
    kit = select_x64_kit()
    if kit:
        name = kit["name"].split("-")[0].strip()
        if name.endswith(" Release"):
            name = name[0:-8]
        path = get_vs_path(name)
        if path:
            return path / "VC\\Auxiliary\\Build\\vcvars64.bat"

    raise FileNotFoundError()


def decode(b: bytes) -> str:
    if platform.system() == "Windows":
        try:
            return b.decode("cp932")
        except:
            return b.decode("utf8")
    else:
        return b.decode("utf-8")


def vcvars64(env) -> Dict[str, str]:
    # %comspec% /k cmd
    comspec = os.environ["comspec"]
    path = [
        os.environ["SystemRoot"] + "\\System32",
        os.environ["SystemRoot"] + "\\System32\\WindowsPowerShell\\v1.0",
    ]
    process = subprocess.Popen(
        [comspec, "/k", get_vcbars(), "&", "set", "&", "exit"],
        stdout=subprocess.PIPE,
        env=env if env!=None else None,
        shell=False,
    )

    stdout = process.stdout
    if not stdout:
        raise Exception()

    # old = {k: v for k, v in os.environ.items()}

    new = {}
    while True:
        rc = process.poll()
        if rc is not None:
            break
        output = stdout.readline()
        line = decode(output)

        if "=" in line:
            k, v = line.strip().split("=", 1)
            # print(k, v)
            new[k.upper()] = v

    # diff(new, old)

    if rc != 0:
        raise Exception(rc)

    return new


def get_env(env) -> Dict[str, str]:
    if platform.system() != "Windows":
        return {}

    # for luarocks detect vc
    filter = (
        "VCINSTALLDIR",
        "PATH",
        "INCLUDE",
        "LIB",
        "LIBPATH",
    )
    return {k: v for k, v in vcvars64(env).items() if (k in filter)}
