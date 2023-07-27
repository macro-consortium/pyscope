import click

import astropy.units as u

@click.command()
@click.option('-p', '--plot', is_flag=True, default=False, show_default=True,
                help='Plot the schedule')
@click.option('-v', '--verbose', is_flag=True, default=False, show_default=True,
                help='Verbose output')
def schedtel(plot, verbose):
    pass

    # Read sch files
    '''sch -> obs'''

    # Define the observer
    '''astroplan observer'''

    # Schedule the observations
    '''astroplan scheduler'''

    # Write the telrun.sls
    '''Each observation into a TelrunScan, then 
    placed into a TelrunFile'''