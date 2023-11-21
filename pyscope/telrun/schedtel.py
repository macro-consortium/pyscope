import configparser
import datetime
import json
import logging
import os
import shlex

import astroplan
import click
import cmcrameri as ccm
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pytz
import smplotlib
import timezonefinder
from astropy import coordinates as coord
from astropy import time as astrotime
from astropy import units as u
from astroquery import mpc
from matplotlib import ticker

from .. import utils
from ..observatory import Observatory
from . import read_sch

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "-c",
    "--catalog",
    type=click.Path(resolve_path=True),
    default="schedules/schedule.cat",
    show_default=True,
    help="A path to a .cat file containing a list of .sch files, a single .sch file, or a list of ObservingBlocks to be scheduled.",
)
@click.option(
    "-i",
    "--ignore-order",
    "ignore_order",
    is_flag=True,
    default=False,
    show_default=True,
    help="Ignore the order of the .sch files in the catalog, acting as if there is only one .sch file. By default, the .sch files are scheduled one at a time.",
)
@click.option(
    "-d",
    "--date",
    type=click.DateTime(formats=["%m-%d-%Y"]),
    default=None,
    show_default=False,
    help="The local date at the observatory of the night to be scheduled. By default, the current date at the observatory location is used.",
)
@click.option(
    "-o",
    "--observatory",
    type=click.Path(resolve_path=True),
    default="./config/observatory.cfg",
    show_default=True,
    help=("The configuration file of the observatory that will execute this schedule"),
)
@click.option(
    "-m",
    "--max-altitude",
    "max_altitude",
    type=click.FloatRange(max=90),
    default=-12,
    show_default=True,
    help="The maximum altitude of the Sun for the night [degrees]. Civil twilight is -6, nautical twilight is -12, and astronomical twilight is -18.",
)
@click.option(
    "-e",
    "--elevation",
    type=click.FloatRange(min=0, max=90, clamp=True),
    default=30,
    show_default=True,
    help='The minimum elevation of all targets [degrees]. This is a "boolean" constraint; that is, there is no understanding of where it is closer to ideal to observe the target. To implement a preference for higher elevation targets, the airmass constraint should be used.',
)
@click.option(
    "-a",
    "--airmass",
    type=click.FloatRange(min=1),
    default=3,
    show_default=True,
    help="The maximum airmass of all targets. If not specified, the airmass is not constrained.",
)
@click.option(
    "-c",
    "--moon-separation",
    type=click.FloatRange(min=0),
    default=30,
    show_default=True,
    help="The minimum angular separation between the Moon and all targets [degrees].",
)
@click.option(
    "-s",
    "--scheduler",
    nargs=2,
    type=(click.Path(exists=True, resolve_path=True), str),
    default=("", ""),
    show_default=False,
    help=(
        "The filepath to and name of an astroplan.Scheduler custom sub-class. By default, the astroplan.PriorityScheduler is used."
    ),
)
@click.option(
    "-g",
    "--gap-time",
    "gap_time",
    type=click.FloatRange(min=0),
    default=60,
    show_default=True,
    help="The maximumum length of time a transition between ObservingBlocks could take [seconds].",
)
@click.option(
    "-r",
    "--resolution",
    type=click.FloatRange(min=0),
    default=5,
    show_default=True,
    help="The time resolution of the schedule [seconds].",
)
@click.option(
    "-f",
    "--filename",
    type=click.Path(),
    default=None,
    show_default=False,
    help="The output file name. The file name is formatted with the UTC date of the first observation in the schedule. By default, it is placed in the current working directory, but if a path is specified, the file will be placed there. WARNING: If the file already exists, it will be overwritten.",
)
@click.option(
    "-t",
    "--telrun",
    is_flag=True,
    default=False,
    show_default=True,
    help="Places the output file in ./schedules/ or in the directory specified by the $TELRUN_EXECUTE environment variable. Causes -f/--filename to be ignored. WARNING: If the file already exists, it will be overwritten.",
)
@click.option(
    "-p",
    "--plot",
    type=click.IntRange(1, 3),
    default=None,
    show_default=False,
    help="Plots the schedule. 1: plots the schedule as a Gantt chart. 2: plots the schedule by target with airmass. 3: plots the schedule on a sky chart.",
)
@click.option(
    "-q", "--quiet", is_flag=True, default=False, show_default=True, help="Quiet output"
)
@click.option(
    "-v", "--verbose", default=0, show_default=True, count=True, help="Verbose output"
)
@click.version_option()
def schedtel_cli(
    catalog,
    ignore_order,
    date,
    observatory,
    max_altitude,
    elevation,
    airmass,
    moon_separation,
    scheduler,
    gap_time,
    resolution,
    filename,
    telrun,
    plot,
    quiet,
    verbose,
):
    # Set up logging
    if quiet:
        level = logging.ERROR
    elif verbose == 0:
        level = logging.WARNING
    elif verbose == 1:
        level = logging.INFO
    elif verbose >= 2:
        level = logging.DEBUG
    logging.basicConfig(level=level)

    logger.info("Starting schedtel")
    logger.debug(f"catalog: {catalog}")
    logger.debug(f"ignore_order: {ignore_order}")
    logger.debug(f"date: {date}")
    logger.debug(f"observatory: {observatory}")
    logger.debug(f"max_altitude: {max_altitude}")
    logger.debug(f"elevation: {elevation}")
    logger.debug(f"airmass: {airmass}")
    logger.debug(f"moon_separation: {moon_separation}")
    logger.debug(f"scheduler: {scheduler}")
    logger.debug(f"gap_time: {gap_time}")
    logger.debug(f"resolution: {resolution}")
    logger.debug(f"filename: {filename}")
    logger.debug(f"telrun: {telrun}")
    logger.debug(f"plot: {plot}")
    logger.debug(f"quiet: {quiet}")
    logger.debug(f"verbose: {verbose}")

    blocks = []

    if os.path.isfile(catalog):
        logger.debug(f"catalog is a file")
        if catalog.endswith(".cat"):
            with open(catalog, "r") as f:
                sch_files = f.read().splitlines()
            for f in sch_files:
                if not os.path.isfile(f):
                    logger.error(f"File {f} in catalog {catalog} does not exist.")
                    return
                blocks.append(read_sch(f))
        elif catalog.endswith(".sch"):
            blocks.append(read_sch(catalog))

    elif type(catalog) in (list, tuple, iter):
        logger.debug(f"catalog is a list")
        for block in catalog:
            if type(block) in (list, tuple, iter):
                for b in block:
                    if type(b) is not astroplan.ObservingBlock:
                        logger.error(
                            f"Object {b} in catalog {catalog} is not an astroplan.ObservingBlock."
                        )
                        return
                blocks.append(block)
            elif type(block) is astroplan.ObservingBlock:
                blocks.append([block])
            else:
                logger.error(
                    f"Object {block} in catalog {catalog} is not an astroplan.ObservingBlock."
                )
                return

    if ignore_order:
        blocks = [
            [blocks[i][j] for i in range(len(blocks)) for j in range(len(blocks[i]))]
        ]

    # Define the observatory
    logger.info("Parsing the observatory")
    if type(observatory) is not astroplan.Observer:
        if type(observatory) is str:
            obs_cfg = configparser.ConfigParser()
            obs_cfg.read(observatory)
            obs_long = obs_cfg.getfloat("site", "longitude")
            obs_lat = obs_cfg.getfloat("site", "latitude")
            obs_height = obs_cfg.getfloat("site", "elevation")
            slew_rate = obs_cfg.getfloat("scheduling", "slew_rate") * u.deg / u.second
            instrument_reconfiguration_times = json.loads(
                obs_cfg.get("scheduling", "instrument_reconfiguration_times")
            )
            instrument_name = obs_cfg.get("site", "instrument_name")
            observatory = astroplan.Observer(
                location=coord.EarthLocation(
                    lon=obs_long * u.deg, lat=obs_lat * u.deg, height=obs_height * u.m
                )
            )
        elif type(observatory) is Observatory:
            obs_long = observatory.observatory_location.lon.deg
            obs_lat = observatory.observatory_location.lat.deg
            obs_height = observatory.observatory_location.height.m
            slew_rate = observatory.slew_rate * u.deg / u.second
            instrument_reconfiguration_times = (
                observatory.instrument_reconfiguration_times
            )
            instrument_name = observatory.instrument_name
            observatory = astroplan.Observer(location=observatory.observatory_location)
        else:
            raise TypeError(
                "Observatory must be, a string, Observatory object, or astroplan.Observer object."
            )

    # Constraints
    logger.info("Defining global constraints")
    global_constraints = [
        astroplan.AltitudeConstraint(min=elevation * u.deg),
        astroplan.AtNightConstraint(max_solar_altitude=max_altitude * u.deg),
        astroplan.AirmassConstraint(max=airmass, boolean_constraint=False),
        astroplan.MoonSeparationConstraint(min=moon_separation * u.deg),
    ]

    # Transitioner
    logger.info("Defining transitioner")
    transitioner = astroplan.Transitioner(
        slew_rate, instrument_reconfiguration_times=instrument_reconfiguration_times
    )

    # Schedule
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
    t1 = t0 + 1 * u.day
    logger.info("Schedule time range: %s to %s" % (t0.iso, t1.iso))

    schedule = astroplan.Schedule(t0, t1)

    # Scheduler
    if scheduler[0] == "":
        logger.info("Using default scheduler: astroplan.PriorityScheduler")
        schedule_handler = astroplan.PriorityScheduler(
            constraints=global_constraints,
            observer=observatory,
            transitioner=transitioner,
            gap_time=gap_time * u.second,
            time_resolution=time_resolution * u.second,
        )
    else:
        logger.info(f"Using custom scheduler: {scheduler[0]}")
        spec = importlib.util.spec_from_file_location(
            scheduler[0].split("/")[-1].split(".")[0], scheduler[0]
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        schedule_handler_class = getattr(module, scheduler[1])
        if not astroplan.Scheduler in schedule_handler_class.__bases__:
            logger.error(
                f"Scheduler {scheduler[0]} does not inherit from astroplan.Scheduler."
            )
            return
        schedule_handler = schedule_handler_class(
            constraints=global_constraints,
            observer=observatory,
            transitioner=transitioner,
            gap_time=gap_time * u.second,
            time_resolution=time_resolution * u.second,
        )

    logger.info("Scheduling ObservingBlocks")
    for i in range(len(blocks)):
        logger.debug("Block group %i of i" % (i + 1, len(blocks)))
        schedule_handler(blocks[i], schedule)

    # Generate schedule table
    schedule_table = schedule.to_table(show_transitions=False, show_unused=False)

    # Update ephem for non-sidereal targets
    for row in schedule_table:
        if (
            row["configuration"]["pm_ra_cosdec"].value != 0
            or row["configuration"]["pm_dec"].value != 0
        ):
            logger.info("Updating ephemeris for %s at scheduled time" % row["target"])
            ephemerides = mpc.MPC.get_ephemeris(
                target=row["target"],
                location=observatory.location,
                start=row["start time (UTC)"],
                number=1,
                proper_motion="sky",
            )
            row["ra"] = ephemerides["RA"][0]
            row["dec"] = ephemerides["DEC"][0]
            row["configuration"]["pm_ra_cosdec"] = (
                ephemerides["dRA cos(Dec)"][0] * u.arcsec / u.hour
            )
            row["configuration"]["pm_dec"] = ephemerides["dDec"][0] * u.arcsec / u.hour

    # Re-assign filenames
    name_dict = {}
    for i in range(len(schedule_table)):
        name = schedule_table[i]["configuration"]["code"]

        if name in name_dict:
            name_dict[name] += 1
        else:
            name_dict[name] = 0

        name += (
            ("%3.3g" % date.strftime("%j")) + "_" + ("%4.4g" % name_dict[name]) + ".fts"
        )
        schedule_table[i]["configuration"]["filename"] = name

    # Write the telrun.ecsv file
    logger.info("Writing schedule to file")
    if filename is None or telrun:
        first_time = astrotime.Time(
            schedule_table[0]["start time (UTC)"], format="iso", scale="utc"
        ).strftime("%m-%d-%Y")
        filename = "telrun_" + first_time + ".ecsv"

    if telrun:
        try:
            path = os.environ.get("TELRUN_EXECUTE")
            logger.info(
                "-t/--telrun flag set, writing schedule to %s from $TELRUN_EXECUTE environment variable"
                % path
            )
        except:
            try:
                path = os.environ.get("OBSERVATORY_HOME") + "/schedules/"
                logger.info(
                    "-t/--telrun flag set, writing schedule to %s from $OBSERVATORY_HOME environment variable"
                    % path
                )
            except:
                path = os.getcwd() + "/schedules/"
                logger.info(
                    "-t/--telrun flag set, writing schedule to %s from current working directory"
                    % path
                )
        if not os.path.isdir(path):
            path = os.getcwd() + "/"
            logger.warning(
                f"Path {path} does not exist, writing to current working directory instead: {path}"
            )
    else:
        path = os.getcwd() + "/"
        logger.info("-t/--telrun flag not set, writing schedule to %s" % path)
    schedule_table.write(path + filename, format="ascii.ecsv", overwrite=True)

    # Plot the schedule
    ax = None
    match plot:
        case 1:  # Gantt chart
            logger.info("Plotting schedule as a Gantt chart")
            ax = plot_schedule_gantt(schedule, observatory)
            return schedule_table, ax
        case 2:  # Plot by target w/ altitude
            logger.info("Plotting schedule by target with airmass")
            ax = astroplan.plots.plot_schedule_airmass(schedule)
            plt.legend()
            return schedule_table, ax
        case 3:  # Sky chart
            logger.info("Plotting schedule on a sky chart")
            ax = plot_schedule_sky(schedule, observatory)
            return schedule_table, ax
        case _:
            logger.info("No plot requested")
            pass

    return schedule_table


@click.command()
@click.argument("schedule_table", type=click.Path(exists=True))
@click.argument("observatory", type=click.Path(exists=True))
@click.version_option()
def plot_schedule_gantt_cli(schedule_table, observatory):
    if type(schedule_table) is not table.Table:
        schedule_table = table.Table.read(schedule_table, format="ascii.ecsv")

    if type(observatory) is not astroplan.Observer:
        if type(observatory) is str:
            obs_cfg = configparser.ConfigParser()
            obs_cfg.read(observatory)
            location = coord.EarthLocation(
                lon=obs_cfg.getfloat("location", "longitude") * u.deg,
                lat=obs_cfg.getfloat("location", "latitude") * u.deg,
                height=obs_cfg.getfloat("location", "elevation") * u.m,
            )
            observatory = astroplan.Observer(location=location)
        elif type(observatory) is Observatory:
            location = observatory.observatory_location
            observatory = astroplan.Observer(location=observatory.observatory_location)
        else:
            raise TypeError(
                "Observatory must be, a string, Observatory object, or astroplan.Observer object."
            )
    else:
        location = observatory.location

    obscodes = np.unique([block["configuration"]["code"] for block in schedule_table])

    date = astrotime.Time(
        schedule_table[0]["start time (UTC)"], format="iso", scale="utc"
    ).datetime
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

    fig, ax = plt.subplots(1, 1, figsize=(12, len(obscodes) / 2))

    for i in range(len(obscodes)):
        plot_blocks = [
            block
            for block in schedule_table
            if block["configuration"]["code"] == obscodes[i]
        ]

        for block in plot_blocks:
            start_time = astrotime.Time(
                block["start time (UTC)"], format="iso", scale="utc"
            )
            end_time = astrotime.Time(
                block["end time (UTC)"], format="iso", scale="utc"
            )
            length_minutes = int((start_time - end_time).sec / 60 + 1)
            times = (
                start_time
                + np.linspace(0, length_minutes, length_minutes, endpoint=True)
                * u.minute
            )

            obj = coord.SkyCoord(ra=block["ra"], dec=block["dec"]).transform_to(
                coord.AltAz(obstime=times, location=location)
            )
            airmass = utils.airmass(obj.alt * u.deg)

            ax.scatter(
                times.datetime,
                i * np.ones(len(times)),
                lw=0,
                marker="s",
                c=airmass,
                cmap=ccm.batlow,
                vmin=1,
                vmax=3,
            )

            scatter = ax.scatter(
                times.datetime,
                len(obscodes) * np.ones(len(times)),
                lw=0,
                marker="s",
                c=airmass,
                cmap=ccm.batlow,
                vmin=1,
                vmax=3,
            )

    obscodes.append("All")

    twilight_times = [
        t0,
        astrotime.Time(observatory.sun_set_time(t0, which="next"), scale="utc"),
        astrotime.Time(
            observatory.twilight_evening_civil(t0, which="next"), scale="utc"
        ),
        astrotime.Time(
            observatory.twilight_evening_nautical(t0, which="next"), scale="utc"
        ),
        astrotime.Time(
            observatory.twilight_evening_astronomical(t0, which="next"), scale="utc"
        ),
        astrotime.Time(
            observatory.twilight_morning_astronomical(t0, which="next"), scale="utc"
        ),
        astrotime.Time(
            observatory.twilight_morning_nautical(t0, which="next"), scale="utc"
        ),
        astrotime.Time(
            observatory.twilight_morning_civil(t0, which="next"), scale="utc"
        ),
        astrotime.Time(observatory.sun_rise_time(t0, which="next"), scale="utc"),
        t1,
    ]
    opacities = [0.8, 0.6, 0.4, 0.2, 0, 0.2, 0.4, 0.6, 0.8]
    for i in range(len(twilight_times) - 1):
        ax.axvspan(
            twilight_times[i].datetime,
            twilight_times[i + 1].datetime,
            color="grey",
            alpha=opacities[i],
        )

    ax.set_xlabel(
        "Time beginning %s [UTC]"
        % (twilight_times[1] - 0.5 * u.hour).strftime("%m-%d-%Y")
    )
    ax.set_xlim(
        [
            (twilight_times[1] - 0.5 * u.hour).datetime,
            (twilight_times[-2].datetime + 0.5 * u.hour).datetime,
        ]
    )
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    ax.xaxis.set_minor_formatter(ticks.NullFormatter())
    ax.xaxis.set_minor_locator(mdates.MinuteLocator(interval=15))
    ax.xtick_params(rotation=45)

    ax.set_ylabel("Observer Code")
    ax.set_ylim([len(obscodes) + 1.5, 0.5])
    ax.yaxis.set_major_formatter(ticker.FixedFormatter(obscodes))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.yaxis.set_minor_formatter(ticks.NullFormatter())
    ax.yaxis.set_minor_locator(ticker.NullLocator())

    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_yticks([1, 1.5, 2, 2.5, 3])
    cbar.set_label("Airmass", rotation=270, labelpad=20)

    ax.set_title(
        "Observing Schedule for %s on %s"
        % (name, twilight_times[1] - 0.5 * u.hour).strftime("%m-%d-%Y")
    )
    ax.grid()

    return ax


@click.command()
@click.argument("schedule_table", type=click.Path(exists=True))
@click.argument("observatory", type=click.Path(exists=True))
@click.version_option()
def plot_schedule_sky_cli():
    objects = []
    times = []
    for i in range(len(schedule_table)):
        if schedule_table[i]["ra"] not in [obj.ra.dms for obj in objects]:
            objects.append(
                coord.SkyCoord(ra=schedule_table[i]["ra"], dec=schedule_table[i]["dec"])
            )
            times.append(
                [
                    (
                        astrotime.Time(
                            schedule_table[i]["start time (UTC)"],
                            format="iso",
                            scale="utc",
                        )
                        + astrotime.Time(
                            schedule_table[i]["end time (UTC)"],
                            format="iso",
                            scale="utc",
                        )
                    )
                    / 2
                ]
            )
        elif schedule_table[i]["dec"] != [obj.ra.dms for obj in objects].index(
            schedule_table[i]["ra"]
        ):
            objects.append(
                coord.SkyCoord(ra=schedule_table[i]["ra"], dec=schedule_table[i]["dec"])
            )
            times.append(
                [
                    (
                        astrotime.Time(
                            schedule_table[i]["start time (UTC)"],
                            format="iso",
                            scale="utc",
                        )
                        + astrotime.Time(
                            schedule_table[i]["end time (UTC)"],
                            format="iso",
                            scale="utc",
                        )
                    )
                    / 2
                ]
            )
        else:
            times[
                [obj.dec.dms for obj in objects].index(schedule_table[i]["dec"])
            ].append(
                (
                    astrotime.Time(
                        schedule_table[i]["start time (UTC)"],
                        format="iso",
                        scale="utc",
                    )
                    + astrotime.Time(
                        schedule_table[i]["end time (UTC)"],
                        format="iso",
                        scale="utc",
                    )
                )
                / 2
            )

    for i in range(len(objects)):
        ax = astroplan.plot_sky(
            astroplan.FixedTarget(objects[i]),
            observatory,
            times[i],
            style_kwargs={
                "color": ccm.batlow(i / (len(objects) - 1)),
                "label": objects[i].to_string("hmsdms"),
            },
        )
    plt.legend()
    return ax


schedtel = schedtel_cli.callback
plot_schedule_gantt = plot_schedule_gantt_cli.callback
plot_schedule_sky = plot_schedule_sky_cli.callback
