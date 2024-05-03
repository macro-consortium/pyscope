import os
from pathlib import Path
import logging

import click

from .synctools import sync_manager
from .telrun_operator import TelrunOperator


@click.command(
    epilog="""Check out the documentation at
               https://pyscope.readthedocs.io/en/latest/
               for more information."""
)
@click.argument(
    "path", type=click.Path(resolve_path=True), default="./", required=False
)
@click.option(
    "-g", "--gui", is_flag=True, default=True, show_default=True, help="Start the GUI"
)
@click.version_option()
def start_telrun_operator_cli(path="./", gui=True):
    telrun = TelrunOperator(config_path=path / "config/telrun.cfg", gui=gui)
    telrun.mainloop()


@click.command(
    epilog="""Check out the documentation at
               https://pyscope.readthedocs.io/en/latest/
               for more information."""
)
@click.option(
    "-a",
    "--do-async",
    is_flag=True,
    default=False,
    show_default=True,
    help="Run the sync manager in async mode",
)
@click.argument(
    "path", type=click.Path(resolve_path=True), default="./", required=False
)
@click.version_option()
def start_sync_manager_cli(path="./", do_async=False):
    logger = logging.getLogger('pyscope')
    logging.basicConfig(level=logging.INFO)

    sync_manager(config=Path(path) / "config/sync.cfg", do_async=do_async)


start_telrun_operator = start_telrun_operator_cli.callback
start_sync_manager = start_sync_manager_cli.callback
