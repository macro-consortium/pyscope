import logging
import os
import platform
import shutil
import subprocess
from pathlib import Path

import click

from .syncfiles import _get_client, _read_syncfiles_cfg, _sync_directory

logger = logging.getLogger(__name__)


@click.command()
@click.argument(
    "path",
    type=click.Path(resolve_path=True, path_type=Path),
    default=Path("pyscope-observatory"),
    required=False,
)
@click.version_option()
def init_telrun_dir_cli(path):
    """test"""
    logger.debug(f"init_telrun_dir(path={path})")

    logger.info("Initializing a telrun home directory at %s" % path)

    if Path(path).exists():
        logger.error(f"Path {path} already exists")
        raise click.Abort()

    logger.info(f"Creating directory {str(path)}")
    Path(path).mkdir()

    logger.info(f"Creating subdirectories")
    Path(path, "config").mkdir()
    Path(path, "schedules").mkdir()
    Path(path, "images").mkdir()
    Path(path, "logs").mkdir()

    logger.info("Creating empty config files")
    shutil.copyfile(
        Path(__file__).parents[1] / "config/telrun.cfg", Path(path, "config/telrun.cfg")
    )

    shutil.copyfile(
        Path(__file__).parents[1] / "config/observatory.cfg",
        Path(path, "config/observatory.cfg"),
    )

    logger.info("Copying default shortcut startup script")
    if platform.system() == "Windows":
        shutil.copyfile(
            Path(__file__).parent / "start_telrun.bat", Path(path, "start_telrun.bat")
        )
    else:
        shutil.copyfile(
            Path(__file__).parent / "start_telrun", Path(path, "start_telrun")
        )

    logger.info("Done")


@click.command()
@click.argument(
    "path",
    type=click.Path(resolve_path=True, exists=True),
    default="./pyscope-observatory/",
    required=False,
)
@click.version_option()
def init_remote_dir_cli(path):
    logger.debug(f"init_remote_dir(path={path})")

    logger.info("Initializing a remote telrun home directory from %s" % path)

    syncfiles_path = Path(path, "config/syncfiles.cfg")
    if not syncfiles_path.exists():
        logger.info("No syncfiles.cfg found, creating one" % path)

        shutil.copyfile(
            Path(__file__).parents[1] / "config/syncfiles.cfg", syncfiles_path
        )

        logger.info(
            "Opening text editor... Please complete all fields and save the file"
        )
        if platform.system() == "Windows":
            subprocess.call(syncfiles_path, shell=True)
        else:
            try:
                logger.info("Trying to open $EDITOR")
                subprocess.call(os.getenv("EDITOR", "vi"), syncfiles_path)
            except:
                logger.warning("Could not open $EDITOR, trying to open vi")
                subprocess.call("vi", syncfiles_path)

        input("Press enter to continue...")

    logger.info("Reading syncfiles.cfg")

    local_config_dir = Path(path, "config")

    (
        uname,
        hostname,
        p,
        k,
        remote_config_dir,
        local_schedules_dir,
        remote_schedules_dir,
        local_images_dir,
        remote_images_dir,
        local_logs_dir,
        remote_logs_dir,
    ) = _read_syncfiles_cfg(Path(local_config_dir, "syncfiles.cfg"))

    logger.info("Performing initial single sync")

    logger.info("Getting SSH and SCP clients")
    ssh, scp = _get_client(uname, hostname, p, k)

    logger.info("Syncing config directory")
    _sync_directory(scp, local_config_dir, remote_config_dir, "send", ".cfg")

    logger.info("Syncing schedules directory")
    _sync_directory(scp, local_schedules_dir, remote_schedules_dir, "both", ".ecsv")

    logger.info("Syncing images directory")
    _sync_directory(
        scp, local_images_dir, remote_images_dir, "send", (".fts", ".fits", ".fit")
    )

    logger.info("Syncing logs directory")
    _sync_directory(scp, local_logs_dir, remote_logs_dir, "send", (".log", ".ecsv"))

    logger.info("Closing SSH and SCP clients")
    ssh.close()

    logger.info("Copying default shortcut startup script")
    if platform.system() == "Windows":
        shutil.copyfile(
            Path(__file__).parent / "start_syncfiles.bat",
            Path(path, "start_syncfiles.bat"),
        )
    else:
        shutil.copyfile(
            Path(__file__).parent / "start_syncfiles", Path(path, "start_syncfiles")
        )


init_telrun_dir = init_telrun_dir_cli.callback
init_remote_dir = init_remote_dir_cli.callback
