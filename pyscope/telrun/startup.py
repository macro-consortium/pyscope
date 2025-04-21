import logging
import os
from pathlib import Path

import click

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
    "-g",
    "--gui",
    is_flag=True,
    default=True,
    show_default=True,
    help="Start the GUI",
)
@click.version_option()
def start_telrun_operator_cli(path="./", gui=True):
    telrun = TelrunOperator(config_path=path / "config/telrun.cfg", gui=gui)
    telrun.mainloop()


start_telrun_operator = start_telrun_operator_cli.callback
