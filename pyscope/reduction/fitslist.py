import logging

import click

logger = logging.getLogger(__name__)

@click.command(epilog='''Check out the documentation at
                https://pyscope.readthedocs.io/ for more
                information.''')
@click.option('-f', '--filt', default='', help='Filter name [default all].')
@click.option('-v', '--verbose', is_flag=True, default=False, show_default=True,
                help='Verbose output.')
@click.version_option(version='0.1.0')
@click.help_option('-h', '--help')
def fitslist_cli():
    pass

fitslist = fitslist_cli.callback