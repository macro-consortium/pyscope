import os

import click

from .syncfiles import syncfiles
from .telrun import TelrunOperator

@click.command()
@click.argument('path', type=click.Path(resolve_path=True),
                default='./', show_default=True,
                required=False,
                help='Path to the telrun home directory')
@click.option('-g', '--gui', is_flag=True, default=True,
            show_default=True, help='Start the GUI')
@click.version_option(version='0.1.0')
@click.help_option('-h', '--help')
def start_telrun(path, gui):
    telrun = TelrunOperator(config_path=os.path.join(path, 'config/telrun.cfg'), gui=gui)
    telrun.mainloop()

@click.command()
@click.argument('path', type=click.Path(resolve_path=True),
                default='./', show_default=True,
                required=False, 
                help='Path to the telrun home directory')
@click.version_option(version='0.1.0')
@click.help_option('-h', '--help')
def start_syncfiles(path):
    syncfiles(config=os.path.join(path, 'config/'))