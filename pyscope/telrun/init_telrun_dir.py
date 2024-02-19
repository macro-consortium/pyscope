import logging
import os
import platform
import shutil
from pathlib import Path

import click

from . import init_queue
from .synctools import sync_manager

logger = logging.getLogger(__name__)


@click.command(
    epilog="""Check out the documentation at
               https://pyscope.readthedocs.io/en/latest/
               for more information."""
)
@click.option(
    "-r",
    "--remote",
    type=bool,
    default=False,
    is_flag=True,
    help="Optionally direct the user through initializing a synced remote telrun home directory.",
)
@click.argument(
    "path",
    type=click.Path(resolve_path=True),
    default="./telhome/",
    required=False,
)
@click.version_option()
def init_telrun_dir_cli(remote=False, path="./telhome/"):
    """
    Initialize a telrun home directory at PATH.

    PATH defaults to ./telhome/ if not specified. If PATH already exists,
    the command will abort. Otherwise, the following directory structure
    will be created::

        PATH/
        |---start_telrun            # A shortcut script to start a TelrunOperator mainloop
        |---config/
        |   |---logging.cfg         # Optional
        |   |---notifications.cfg   # Optional
        |   |---observatory.cfg
        |   |---sync_manager.cfg    # Optional
        |   |---telrun.cfg
        |
        |---images/                 # Images captured by TelrunOperator are saved here
        |   |---im1.fts
        |   |---autofocus/
        |   |---calibrations/
        |   |   |---masters/        # Master calibration images, created by cal scripts
        |   |   |   |---YYYY-MM-DD/     # Timestamped calibration sets
        |   |   |---YYYY-MM-DD/     # Individual calibration images
        |   |---raw_archive/        # Optional, but recommended. Backup of raw images
        |   |---recenter/
        |   |---reduced/            # Optional. Where reduced images are saved if not done in-place
        |
        |---logs/                   # TelrunOperator logs and auto-generated reports are saved here if requested
        |   |---telrun_status.json  # A JSON file containing the current status of TelrunOperator
        |
        |---schedules/
        |   |---aaa000.sch          # A schedule file for schedtel
        |   |---schedules.cat       # A catalog of sch files to be scheduled
        |   |---queue.ecsv          # A queue of unscheduled blocks
        |   |---completed/          # sch files that have been parsed and scheduled
        |   |---execute/            # Where schedtel puts schedules to be executed
        |
        |---tmp/                    # Temporary files are saved here, not synced by default

    Parameters
    ----------
    remote : `bool`, optional, default=False
        If True, the user will be directed through initializing a synced remote telrun home directory

    path : `str`, optional, default="./telhome/"
        The path to the telrun home directory to be created

    Returns
    -------
    `None`

    See Also
    --------
    pyscope.telrun.TelrunOperator : The main class for running a telescope
    pyscope.telrun.schedtel : Schedule a sch file
    pyscope.telrun.sync_manager : Sync a local telrun home directory with a remote one

    """

    logger.debug(f"init_telrun_dir(remote={remote}, path={path})")

    path = Path(path).resolve()
    logger.info("Initializing a telrun home directory at %s" % path)

    if path.exists():
        logger.error(f"Path {path} already exists")
        raise click.Abort()

    logger.info(f"Creating directory {path}")
    path.mkdir()

    logger.info("Creating config directory")
    (path / "config").mkdir()
    logger.info("Creating empty config files")
    shutil.copyfile(
        Path(os.path.dirname(__file__)) / "../bin/cfg_templates/telrun-empty.cfg",
        path / "config/telrun.cfg",
    )
    shutil.copyfile(
        Path(os.path.dirname(__file__)) / "../bin/cfg_templates/observatory-empty.cfg",
        path / "config/observatory.cfg",
    )
    shutil.copyfile(
        Path(os.path.dirname(__file__)) / "../bin/cfg_templates/logging-empty.cfg",
        path / "config/logging.cfg",
    )
    shutil.copyfile(
        Path(os.path.dirname(__file__))
        / "../bin/cfg_templates/notifications-empty.cfg",
        path / "config/notifications.cfg",
    )
    shutil.copyfile(
        Path(os.path.dirname(__file__)) / "../bin/cfg_templates/sync_manager-empty.cfg",
        path / "config/sync_manager.cfg",
    )

    logger.info("Creating images directory")
    (path / "images").mkdir()
    (path / "images" / "autofocus").mkdir()
    (path / "images" / "calibrations").mkdir()
    (path / "images" / "calibrations" / "masters").mkdir()
    (path / "images" / "raw_archive").mkdir()
    (path / "images" / "reduced").mkdir()

    logger.info("Creating logs directory")
    (path / "logs").mkdir()

    logger.info("Creating schedules directory")
    (path / "schedules").mkdir()
    (path / "schedules" / "completed").mkdir()
    (path / "schedules" / "execute").mkdir()
    (path / "schedules" / "schedules.cat").touch()
    # init_queue(path / "schedules" / "queue.ecsv")

    logger.info("Copying default shortcut startup script")
    if platform.system() == "Windows":
        shutil.copyfile(
            Path(os.path.dirname(__file__)) / "../bin/scripts/start_telrun.bat",
            path / "start_telrun.bat",
        )
    else:
        shutil.copyfile(
            Path(os.path.dirname(__file__)) / "../bin/scripts/start_telrun",
            path / "start_telrun",
        )

    if remote:
        logger.info(
            "Remote option selected, directing user through remote initialization"
        )
        logger.info("Opening config files for editing")
        if platform.system() == "Windows":
            os.system(path / "config/sync_manager.cfg")
        else:
            try:
                logger.info(
                    "Trying to open $EDITOR: '%s %s'"
                    % (os.getenv("EDITOR"), path / "config/sync_manager.cfg")
                )
                os.system(
                    "%s %s" % (os.getenv("EDITOR"), path / "config/sync_manager.cfg")
                )
            except:
                logger.warning(
                    "Could not open $EDITOR, trying to open vi: 'vi %s'"
                    % (path / "config/sync_manager.cfg")
                )
                try:
                    os.system("vi " + str(path / "config/sync_manager.cfg"))
                except:
                    logger.error(
                        "Could not open vi, please edit the config files manually"
                    )
                    logger.error(
                        "You can find the documentation at https://pyscope.readthedocs.io/en/latest/"
                    )
                    return

        _ = input("Press any key to continue with syncing directory...")

        logger.info("Syncing directory")
        sync_manager(config=path / "config/sync_manager.cfg", do_once=True)

        logger.info("Copying default shortcut startup script")
        if platform.system() == "Windows":
            shutil.copyfile(
                Path(os.path.dirname(__file__))
                / "../bin/scripts/start_sync_manager.bat",
                path / "start_sync_manager.bat",
            )
        else:
            shutil.copyfile(
                Path(os.path.dirname(__file__)) / "../bin/scripts/start_sync_manager",
                path / "start_sync_manager",
            )

    logger.info("Done")


init_telrun_dir = init_telrun_dir_cli.callback
