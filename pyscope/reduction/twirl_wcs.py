import click


@click.command(
    epilog="""Check out the documentation at
                https://pyscope.readthedocs.io/ for more
                information."""
)
@click.version_option()
def twirl_wcs_cli():
    pass


twirl_wcs = twirl_wcs_cli.callback
