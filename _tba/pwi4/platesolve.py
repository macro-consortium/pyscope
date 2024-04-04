"""
This module wraps the PlateSolve3 command-line executable to provide
all-sky star matching of telescope images. It is used by the pwi4_build_model
script to determine where a telescope is pointing when building a pointing
model.
"""

import os.path
import platform
import tempfile
from subprocess import PIPE, Popen

# Point this to the location of the "ps3cli.exe" executable
PS3CLI_EXE = os.path.expanduser("~/ps3cli/ps3cli.exe")

# For testing purposes...
# PS3CLI_EXE = r"C:\Users\kmi\Desktop\Planewave work\Code\PWGit\PWCode\ps3cli\bin\Debug\ps3cli.exe"


# Set this to the path where the PlateSolve catalogs are located.
# The directory specified here should contain "UC4" and "Orca" subdirectories.
# If this is None, we will try to use the default catalog location
PS3_CATALOG = None


def is_linux():
    return platform.system() == "Linux"


def get_default_catalog_location():
    if is_linux():
        return os.path.expanduser("~/Kepler")
    else:
        return os.path.expanduser("~\\Documents\\Kepler")


def platesolve(image_file, arcsec_per_pixel):
    stdout_destination = None  # Replace with PIPE if we want to capture the output rather than displaying on the console

    output_file_path = os.path.join(tempfile.gettempdir(), "ps3cli_results.txt")

    if PS3_CATALOG is None:
        catalog_path = get_default_catalog_location()
    else:
        catalog_path = PS3_CATALOG

    args = [
        PS3CLI_EXE,
        image_file,
        str(arcsec_per_pixel),
        output_file_path,
        catalog_path,
    ]

    if is_linux():
        # Linux systems need to run ps3cli via the mono runtime,
        # so add that to the beginning of the command/argument list
        args.insert(0, "mono")

    process = Popen(args, stdout=stdout_destination, stderr=PIPE)

    (stdout, stderr) = (
        process.communicate()
    )  # Obtain stdout and stderr output from the wcs tool
    exit_code = process.wait()  # Wait for process to complete and obtain the exit code

    if exit_code != 0:
        raise Exception(
            "Error finding solution.\n"
            + "Exit code: "
            + str(exit_code)
            + "\n"
            + "Error output: "
            + stderr
        )

    return parse_platesolve_output(output_file_path)


def parse_platesolve_output(output_file):
    f = open(output_file)

    results = {}

    for line in f.readlines():
        line = line.strip()
        if line == "":
            continue

        fields = line.split("=")
        if len(fields) != 2:
            continue

        keyword, value = fields

        results[keyword] = float(value)

    return results
