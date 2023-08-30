import os
import platform
import subprocess
from tarfile import TarFile
from zipfile import ZipFile


def setup_server():
    if platform.system() == "Darwin":
        sys_name = "macos-x64.zip"
    elif platform.system() == "Linux":
        sys_name = "linux"

        if "arm" in platform.machine():
            sys_name += "-armhf.tar.xz"
        elif "aarch64" in platform.machine():
            sys_name += "-aarch64.tar.xz"
        elif "x86_64" in platform.machine():
            sys_name += "-x64.tar.xz"

    elif platform.system() == "Windows":
        sys_name = "windows"

        if "x86_64" in platform.machine():
            sys_name += "-x86.zip"
        elif "x64" in platform.machine():
            sys_name += "-x64.zip"

    else:
        raise Exception("Unsupported platform")

    if not os.path.isfile("./ascom.alpaca.simulators." + sys_name):
        p = subprocess.check_output(
            (
                "gh release download v0.3.1 --repo ASCOMInitiative/ASCOM.Alpaca.Simulators"
            ).split()
        )

    if not os.path.exists("./ascom.alpaca.simulators." + sys_name):
        os.mkdir("./ascom.alpaca.simulators." + sys_name)

    if sys_name.endswith(".zip"):
        with ZipFile("./ascom.alpaca.simulators." + sys_name + ".zip", "r") as zipObj:
            zipObj.extractall("./ascom.alpaca.simulators." + sys_name)
    elif sys_name.endswith(".tar.xz"):
        with TarFile.open(
            "./ascom.alpaca.simulators." + sys_name + ".tar.xz", "r"
        ) as tarObj:
            tarObj.extractall("./ascom.alpaca.simulators." + sys_name)

    if platform.system() == "Darwin":
        return subprocess.Popen(
            (
                "sudo ./ascom.alpaca.simulators."
                + sys_name
                + "/ascom.alpaca.simulators"
            ).split()
        )
    else:
        return subprocess.Popen(
            (
                "./ascom.alpaca.simulators." + sys_name + "/ascom.alpaca.simulators"
            ).split(),
            prexec_fn=os.setsid,
        )


def teardown_server(cmd):
    os.killpg(os.getpgid(cmd.pid), signal.SIGTERM)
