import configparser
import datetime
import logging
import os
import zoneinfo

import astroplan
import click
import numpy as np
import prettytable
import timezonefinder
from astropy import coordinates as coord
from astropy import table
from astropy import time as astrotime
from astropy import units as u
from astroquery.mpc import MPC

from ..observatory import Observatory

logger = logging.getLogger(__name__)


@click.command(
    epilog="""Check out the documentation at
               https://pyscope.readthedocs.io/en/latest/
               for more information."""
)
@click.option(
    "-s",
    "--source",
    type=str,
    help="""Source name. 
    Is resolved by astropy.coordinates.SkyCoord.from_name() first, then
    if not found, attempts to check the Minor Planet Center via astroquery.
    Finally, it attempts to use astropy.coordinates.get_body for solar system
    bodies. If no source is given, then dawn and dusk times are calculated for the
    observatory.""",
)
@click.option(
    "-d",
    "--date",
    type=str,
    help="""Date of observation [YYYY-MM-DD]. 
    If none is given, the current date at the observatory is used.""",
)
@click.option(
    "-o",
    "--observatory",
    type=click.Path(resolve_path=True, dir_okay=False, exists=True),
    default="./config/observatory.cfg",
    show_default=True,
    help="""Observatory configuration file.""",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    type=click.IntRange(0, 1),  # Range can be changed
    help="Increase verbosity",
)
def rst_cli(source=None, date=None, observatory="./config/observatory.cfg", verbose=0):
    """Calculate the rise, set, and transit times for a given source or dusk and
    dawn times for the observatory.\b

    The observatory configuration file is required to calculate the rise, set, and
    transit times for a given source. If no source is given, then the dusk and dawn
    times are calculated for the observatory. If no date is given, then the current
    date at the location of the observatory is used. The source is first resolved
    by `astropy.coordinates.SkyCoord.from_name` and if not found, the `astroquery.mpc.MPCClass`
    is used. Finally, if the source is not found, then `astropy.coordinates.get_body` is used
    for solar system bodies. If the source is still not found, then the program exits with an
    error message.

    .. warning::
        The rise, set, and transit times may be inaccurate for high proper motion
        bodies and solar system bodies. Other sources are generally accurate to
        within a few minutes.

    Parameters
    ----------
    source : str, optional
        Source name.

    date : str [YYYY-MM-DD], optional
        Date of observation. If none is given, the current date at the observatory is used.

    observatory : str or `~pyscope.observatory.Observatory`, default='./config/observatory.cfg'
        Observatory configuration file or :py:class:`~pyscope.observatory.Observatory` object.

    verbose : int, {-1, 0, 1}, default=0
        Increase verbosity.

    Returns
    -------
    list
        List of tuples containing the event name and a `~astropy.time.Time` object.

    Raises
    ------
    `click.BadParameter`

    See Also
    --------
    pyscope.telrun.exoplanet_transits
    pyscope.telrun.schedtel
    astropy.coordinates.SkyCoord.from_name
    astroquery.mpc.MPCClass.get_ephemeris

    Examples
    --------
    Compute the rise, set, and transit times for M64 on 2024-01-30.

    .. code-block:: python

        >>> from pyscope.telrun import rst
        >>> tbl = rst(observatory="../tests/observatory.cfg", source="M64", date="2024-01-30")
        Times from: 2024-01-30 12:00 (MST), 2024-01-30 19:00 (UTC)
        +-----------------------------+-------+-------+-------+
        |                        Time | Local |  UTC  |  LST  |
        +-----------------------------+-------+-------+-------+
        |                      Sunset | 17:50 | 00:50 |  2:07 |
        |        Civil Twilight Start | 18:20 | 01:20 |  2:37 |
        |     Nautical Twilight Start | 18:49 | 01:49 |  3:06 |
        | Astronomical Twilight Start | 19:18 | 02:18 |  3:35 |
        |                    M64 Rise | 21:44 | 04:44 |  6:02 |
        |                 M64 Transit | 04:39 | 11:39 | 12:58 |
        |   Astronomical Twilight End | 05:52 | 12:52 | 14:11 |
        |       Nautical Twilight End | 06:21 | 13:21 | 14:40 |
        |          Civil Twilight End | 06:50 | 13:50 | 15:09 |
        |                     Sunrise | 07:20 | 14:20 | 15:39 |
        |                     M64 Set | 11:34 | 18:34 | 19:54 |
        +-----------------------------+-------+-------+-------+

    Perform the same calculation, but on the command line.

    .. code-block:: shell

        $ rst -o ../tests/observatory.cfg -s M64 -d 2024-01-30
        Times from: 2024-01-30 12:00 (MST), 2024-01-30 19:00 (UTC)
        +-----------------------------+-------+-------+-------+
        |                        Time | Local |  UTC  |  LST  |
        +-----------------------------+-------+-------+-------+
        |                      Sunset | 17:50 | 00:50 |  2:07 |
        |        Civil Twilight Start | 18:20 | 01:20 |  2:37 |
        |     Nautical Twilight Start | 18:49 | 01:49 |  3:06 |
        | Astronomical Twilight Start | 19:18 | 02:18 |  3:35 |
        |                    M64 Rise | 21:44 | 04:44 |  6:02 |
        |                 M64 Transit | 04:39 | 11:39 | 12:58 |
        |   Astronomical Twilight End | 05:52 | 12:52 | 14:11 |
        |       Nautical Twilight End | 06:21 | 13:21 | 14:40 |
        |          Civil Twilight End | 06:50 | 13:50 | 15:09 |
        |                     Sunrise | 07:20 | 14:20 | 15:39 |
        |                     M64 Set | 11:34 | 18:34 | 19:54 |
        +-----------------------------+-------+-------+-------+

    """

    logger.setLevel(int(10 * (2 - verbose)))
    logger.addHandler(logging.StreamHandler())
    logger.debug(f"Verbosity level set to {verbose}")
    logger.debug(
        f"""rst(source={source}, date={date}, observatory={observatory}
        verbose={verbose})"""
    )

    if type(observatory) is str:
        observatory = os.path.abspath(observatory)
        if os.path.exists(observatory):
            config = configparser.ConfigParser()
            config.read(observatory)
            lat = coord.Latitude(config["site"]["latitude"], unit=u.deg)
            lon = coord.Longitude(
                config["site"]["longitude"], unit=u.deg, wrap_angle=180 * u.deg
            )
            name = config.get("site", "name", fallback="pyscope observatory")
        else:
            raise click.BadParameter(
                "Observatory configuration file does not exist: %s" % observatory
            )
    elif type(observatory) is Observatory:
        lat = observatory.observatory_location.lat
        lon = observatory.observatory_location.lon
        name = observatory.instrument_name
    else:
        raise click.BadParameter("Observatory must be a string or Observatory object.")
    logger.debug(f"lat = {lat}")
    logger.debug(f"lon = {lon}")
    logger.debug(f"name = {name}")

    tz = timezonefinder.TimezoneFinder().timezone_at(lng=lon.deg, lat=lat.deg)
    tz = zoneinfo.ZoneInfo(tz)
    logger.debug(f"tz = {tz}")

    if date is None:
        logger.debug("Using current date at observatory location")
        date = datetime.datetime.now()
    else:
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
    date = datetime.datetime(date.year, date.month, date.day, 12, 0, 0, tzinfo=tz)

    t0 = astrotime.Time(
        datetime.datetime(date.year, date.month, date.day, 12, 0, 0, tzinfo=tz),
        format="datetime",
    )
    logger.debug(f"t0 = {t0}")

    observer = astroplan.Observer(
        location=coord.EarthLocation.from_geodetic(lon, lat), name=name
    )

    horizon = (
        ("Sunset", observer.sun_set_time(t0, which="nearest")),
        ("Sunrise", observer.sun_rise_time(t0, which="next")),
    )
    civil_twilight = (
        (
            "Civil Twilight Start",
            observer.sun_set_time(t0, which="nearest", horizon=-6 * u.deg),
        ),
        (
            "Civil Twilight End",
            observer.sun_rise_time(t0, which="next", horizon=-6 * u.deg),
        ),
    )
    nautical_twilight = (
        (
            "Nautical Twilight Start",
            observer.sun_set_time(t0, which="nearest", horizon=-12 * u.deg),
        ),
        (
            "Nautical Twilight End",
            observer.sun_rise_time(t0, which="next", horizon=-12 * u.deg),
        ),
    )
    astronomical_twilight = (
        (
            "Astronomical Twilight Start",
            observer.sun_set_time(t0, which="nearest", horizon=-18 * u.deg),
        ),
        (
            "Astronomical Twilight End",
            observer.sun_rise_time(t0, which="next", horizon=-18 * u.deg),
        ),
    )

    times = [
        horizon[0],
        horizon[1],
        civil_twilight[0],
        civil_twilight[1],
        nautical_twilight[0],
        nautical_twilight[1],
        astronomical_twilight[0],
        astronomical_twilight[1],
    ]

    if source is not None:
        try:
            obj = coord.SkyCoord.from_name(source)
        except coord.name_resolve.NameResolveError:
            logger.debug(f"Could not resolve {source} by name. Attempting MPC query.")
            try:
                eph = MPC.get_ephemeris(
                    source,
                    start=t0 + 0.5 * u.day,
                    location=observer.location,
                    proper_motion="sky",
                )
                obj = coord.SkyCoord(
                    ra=eph["RA"],
                    dec=eph["Dec"],
                    unit=("deg", "deg"),
                    pm_ra_cosdec=eph["dRA cos(Dec)"],
                    pm_dec=eph["dDec"],
                    frame="icrs",
                )
                logger.warning(
                    f"""Could not resolve {source} by name. Using MPC query.
                    Note that rise-set times may be inaccurate for high PM bodies."""
                )
            except:
                try:
                    obj = coord.get_body(source, t0 + 0.5 * u.day, observer.location)
                    logger.warning(
                        f"""Could not resolve {source} by name or MPC query. Using get_body query.
                        Note that rise-set times may be inaccurate for solar system bodies."""
                    )
                except:
                    click.echo(
                        f"Could not resolve {source} by name, MPC query, or get_body query."
                    )
                    click.Abort()
                    return
        logger.debug(f"obj = {obj}")

        rise_time = (
            "%s Rise" % source,
            observer.target_rise_time(t0, obj, which="next"),
        )
        transit_time = (
            "%s Transit" % source,
            observer.target_meridian_transit_time(t0, obj, which="next"),
        )
        set_time = ("%s Set" % source, observer.target_set_time(t0, obj, which="next"))

        logger.debug(f"rise_time = {rise_time}")
        logger.debug(f"transit_time = {transit_time}")
        logger.debug(f"set_time = {set_time}")

        logger.debug(type(transit_time[1].value))

        if not isinstance(rise_time[1].value, np.ma.MaskedArray):
            times.append(rise_time)
        if not isinstance(transit_time[1].value, np.ma.MaskedArray):
            times.append(transit_time)
        if not isinstance(set_time[1].value, np.ma.MaskedArray):
            times.append(set_time)

        if isinstance(rise_time[1].value, np.ma.MaskedArray) and isinstance(
            set_time[1].value, np.ma.MaskedArray
        ):
            if isinstance(transit_time[1].value, np.ma.MaskedArray):
                logger.warning("This source never rises above the horizon.")
            else:
                logger.warning("This source is circumpolar.")

    times.sort(key=lambda x: x[1].jd)

    tbl = prettytable.PrettyTable()
    tbl.field_names = ["Time", "Local", "UTC", "LST"]
    tbl.align["Time"] = "r"

    for t in times:
        tbl.add_row(
            [
                t[0],
                t[1].to_datetime(timezone=tz).strftime("%H:%M"),
                t[1].strftime("%H:%M"),
                observer.local_sidereal_time(t[1]).to_string(
                    precision=0, sep=":", fields=2
                ),
            ]
        )

    if verbose > -1:
        click.echo(
            f"Times from: {date.strftime('%Y-%m-%d %H:%M (%Z)')}, {t0.strftime('%Y-%m-%d %H:%M (UTC)')}"
        )
        click.echo(tbl)

    return times


rst = rst_cli.callback
