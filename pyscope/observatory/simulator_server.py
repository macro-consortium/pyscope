import multiprocessing
import os
import platform
import signal
import subprocess
from pathlib import Path
from tarfile import TarFile
from zipfile import ZipFile

# import oschmod


class SimulatorServer:
    def __init__(self, force_update=False):
        """
        Class for starting the ASCOM Alpaca Simulators server.

        This classhandles downloading, extracting, and launching the ASCOM Alpaca Simulators
        server executable appropriate for the host's operating system and architecture.
        Ensures correct version is downloaded and forces updating if specified.

        Parameters
        ----------
        force_update : bool, default : `False`, optional
            If `True`, forces download of the ASCOM Alpaca Simulators server executable.
            If `False`, checks if the executable exists and skips download if it does.

        Raises
        ------
        Exception
            If the host's operating system is not supported.

        Notes
        -----
        The server executable is downloaded from the ASCOM Initiative GitHub repository found `here <https://github.com/ASCOMInitiative/ASCOM.Alpaca.Simulators>`_,
        and is from the latest release version of v0.3.1.
        Currently supported operating systems are:
        - macOS (Darwin)
        - Linux (x86_64, armhf, aarch64)
        - Windows (x86, x64)
        """
        if platform.system() == "Darwin":
            sys_name = "macos-x64"
            zip_type = ".zip"
            executable = "ascom.alpaca.simulators"
        elif platform.system() == "Linux":
            sys_name = "linux"
            zip_type = ".tar.xz"
            executable = "ascom.alpaca.simulators"

            if "arm" in platform.machine():
                sys_name += "-armhf"
            elif "aarch64" in platform.machine():
                sys_name += "-aarch64"
            elif "x86_64" in platform.machine():
                sys_name += "-x64"

        elif platform.system() == "Windows":
            sys_name = "windows"
            zip_type = ".zip"
            executable = "ascom.alpaca.simulators.exe"

            if "86" in platform.machine():
                sys_name += "-x86"
            elif "64" in platform.machine():
                sys_name += "-x64"

        else:
            raise Exception("Unsupported platform")

        dirname = Path("ascom.alpaca.simulators." + sys_name)

        if not os.path.exists(dirname) or force_update:

            p = subprocess.check_output(
                f"""gh release download v0.3.1 --repo ASCOMInitiative/ASCOM.Alpaca.Simulators --skip-existing --pattern {dirname}{zip_type}""",
                shell=True,
            )

            if zip_type == ".zip":
                with ZipFile(str(dirname) + zip_type, "r") as zipObj:
                    zipObj.extractall()
            elif zip_type == ".tar.xz":
                with TarFile.open(str(dirname) + zip_type, "r") as tarObj:
                    tarObj.extractall()

            oschmod.set_mode(str(dirname), 0o755)

        current_dir = os.getcwd()
        os.chdir(dirname)

        if platform.system() == "Darwin" or platform.system() == "Linux":
            self.process = subprocess.Popen(
                ("sudo ./" + str(executable)),
                preexec_fn=os.setpgrp,
                start_new_session=True,
                stderr=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                shell=True,
            )
        else:
            self.process = subprocess.Popen(
                str(executable),
                # preexec_fn=os.setpgrp,
                start_new_session=True,
                stderr=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                shell=True,
            )

        self.executable = dirname / executable

        os.chdir(current_dir)

    def __del__(self):
        """
        Automatically kills the server process when the object is deleted.
        """
        if platform.system() == "Darwin" or platform.system() == "Linux":
            # self.process.kill() # doesn't work since sudo is needed
            subprocess.Popen(
                f"sudo kill {(os.getpgid(self.process.pid) + 1)}", shell=True
            )
        else:
            self.process.kill()
            # subprocess.Popen(f"taskkill /PID {(os.getpgid(self.process.pid)+1)} /F", shell=True)
