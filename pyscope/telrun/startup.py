import os

import click

from .syncfiles import syncfiles
from .telrun_operator import TelrunOperator


@click.command()
@click.argument(
    "path", type=click.Path(resolve_path=True), default="./", required=False
)
@click.option(
    "-g", "--gui", is_flag=True, default=True, show_default=True, help="Start the GUI"
)
@click.version_option(version="0.1.0")
@click.help_option("-h", "--help")
def start_telrun_cli(path, gui):
    telrun = TelrunOperator(
        config_path=os.path.join(path, "config/telrun.cfg"), gui=gui
    )
    telrun.mainloop()


@click.command()
@click.argument(
    "path", type=click.Path(resolve_path=True), default="./", required=False
)
@click.version_option(version="0.1.0")
@click.help_option("-h", "--help")
def start_syncfiles_cli(path):
    syncfiles(config=os.path.join(path, "config/"))


start_telrun = start_telrun_cli.callback
start_syncfiles = start_syncfiles_cli.callback
