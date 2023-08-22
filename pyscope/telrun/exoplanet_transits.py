import configparser
import datetime
import logging
import timezonefinder

from astropy import coordinates as coord, time as astrotime, units as u
from astroquery.ipac.nexsci.nasa_exoplanet_archive import NasaExoplanetArchive
import click
import prettytable

from ..observatory import Observatory

logger = logging.getLogger(__name__)

@click.command(epilog='''Check out the documentation at
               https://pyscope.readthedocs.io/en/latest/
               for more information.''')
@click.option('-f', '--filt', type=str, default='g', show_default=True,
              help='SDSS filter magnitude to check')
@click.option('-m', '--max-mag', type=int, default=15,
              show_default=True, help='Maximum magnitude of host star')
@click.option('-t', '--transit-depth', type=float, default=0.02,
              show_default=True, help='Minimum transit depth')
@click.option('-p', '--transit-depth-percent', type=float, 
            help='Minimum transit depth in percent. Overrides -t option.')
@click.option('-d', '--date', type=str, 
              help='''Date of observation in YYYY-MM-DD format. 
              If not specified, defaults to today.''')
@click.option('-o', '--observatory', type=click.Path(exists=True, dir_okay=False,
                resolve_path=True), default='./config/observatory.cfg',
                help='Path to observatory config file')
@click.option('-v', '--verbose', count=True,
              type=click.IntRange(0, 1), # Range can be changed
              help='Increase verbosity')
def exoplanet_transits_cli(filt, max_mag, transit_depth, transit_depth_percent,
        date, observatory, verbose):
    '''

    Acknowledgements: This code was adapted from Aurora Hiveley's
    exoplanet_transits.py script.
    '''

    logger.setLevel(int(10 * (1 - verbose))) # Change range via 3
    logger.debug(f'Verbosity level set to {verbose}')
    logger.debug(f'''exoplanet_transits_cli(max_mag={max_mag},
                transit_depth={transit_depth},
                transit_depth_percent={transit_depth_percent},
                date={date},
                observatory={observatory},
                verbose={verbose})''')

    if type(observatory) is str:
        observatory = Observatory(config_path=observatory)
    elif type(observatory) is Observatory:
        pass
    else:
        raise TypeError(
            "Observatory must be, a string, Observatory object, or astroplan.Observer object."
        )
    
    if transit_depth_percent is not None:
        transit_depth = np.log10(1+transit_depth_percent/100)/0.4

    if date is None:
        logger.info("Using current date at observatory location")
        tz = timezonefinder.TimezoneFinder().timezone_at(lng=observatory.observatory_location.lon.deg,
            lat=observatory.observatory_location.lat.deg)
        date = datetime.datetime.now(pytz.timezone(tz))

    t0 = (
        astrotime.Time(
            datetime.datetime(date.year, date.month, date.day, 12, 0, 0),
            format="datetime",
            scale="utc",
        )
        - (
            (
                astrotime.Time(date, format="datetime", scale="utc")
                - astrotime.Time.now()
            ).day
            % 1
        )
        * u.day
    )
    t1 = t0 + 1 * u.day
    logger.info("Searching UT range: %s to %s" % (t0.iso, t1.iso))

    min_ra = observatory.lst(t=t0).to(u.deg).value
    max_ra = observatory.lst(t=t1).to(u.deg).value
    logger.info("Searching LST range: %s to %s" % (min_ra, max_ra))

    min_dec = np.max(observatory.observatory_location.lat.deg - 
    (90-observatory.min_altitude), -90)
    max_dec = np.min(observatory.observatory_location.lat.deg + 
    (90-observatory.min_altitude), 90)
    logger.info("Searching declination range: %s to %s" % (min_dec, max_dec))

    transit_depth_percent = 100*(10**(0.4*transit_depth)-1)

    table = NasaExoplanetArchive.query_criteria(
        table="PS", 
        select=f"""pl_name,hostname,
                ra,dec,
                sy_{filt}mag,
                pl_tranmid,
                pl_orbper,
                pl_trandep,
                pl_trandur,
                rowupdate,
                st_nphot
                """,
        where=f"""
                pl_controv_flag=0 and
                tran_flag=1 and
                ra between {min_ra} and {max_ra} and
                dec between {min_dec} and {max_dec} and
                sy_{filt}mag <= {max_mag} and
                pl_trandep >= {transit_depth_percent}
                """,
        order=f"pl_trandep desc")

    print_table = []

    for exo, i in enumerate(table):
        t_until_next_transit = (exo['pl_orbper']*u.day -
        (t0 - exo['pl_tranmid']))

        if t_until_next_transit > (t1 - t0):
            logger.info(f"Removing {exo['pl_name']} because it is not transiting between {t0.iso} and {t1.iso}")
            t.remove_row(i)
            continue
        
        print_table.append([
            exo['pl_name'],
            exo['hostname'],
            exo['sky_coord'].ra.hms,
            exo['sky_coord'].dec.dms,
            exo[f'sy_{filt}mag'],
            exo['pl_tranmid'],
            exo['pl_orbper'],
            exo['pl_trandep'],
            exo['pl_trandur'],
            exo['rowupdate'],
            exo['st_nphot']
        ])
    
    table = prettytable.PrettyTable()
    table.add_rows(print_table)
    table.set_style(prettytable.SINGLE_BORDER)
    table.field_names = [
        "Planet Name",
        "Host Name",
        "RA",
        "Dec",
        f"{filt} mag",
        "Reference Epoch [JD]",
        "Orbital Period [d]",
        f"Transit Depth [%]",
        "Transit Duration [h]",
        "Last Updated",
        "# of Photometric Observations"
    ]

    T.align["Planet Name"] = "l"
    click.echo(table)
    click.echo()
    clic, echo(f"Number of exoplanets = {len(print_table)}")

    return table

exoplanet_transits = exoplanet_transits_cli.callback