import logging

import astroplan
import click
from astropy import coordinates as coord

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
    default="",
    required=True,
    help="""Source name to resolve coordinates or a
              pair of ICRS ra,dec coordinates: hh:mm:ss,dd:mm:ss or any format
              that initializes an astropy.coordinates.SkyCoord object.""",
)
@click.option(
    "-f",
    "--filters",
    type=str,
    required=True,
    help="""Filters to use. Multiple filters can be
            specified by repeating the option, e.g. -f b -f g -f r""",
)
@click.option(
    "-e",
    "--exp-times",
    type=float,
    required=True,
    multiple=True,
    help="""Exposure times to use for each filter. Multiple exposure
            times can be specified by repeating the option, e.g. -e 10 -e 20.
            Must match length of filters.""",
)
@click.option(
    "-o",
    "--observer",
    nargs=2,
    type=str,
    default=("", ""),
    required=True,
    help="""Observer name and 3-character code.""",
)
@click.option(
    "-O",
    "--overlap",
    type=float,
    default=5,
    show_default=True,
    help="""Overlap between pointings (arcmin).""",
)
@click.option(
    "-F",
    "--fov",
    nargs=2,
    type=float,
    default=(20, 20),
    show_default=True,
    help="""Field of view (arcmin).""",
)
@click.option(
    "-g",
    "--grid-size",
    nargs=2,
    type=int,
    default=(3, 3),
    show_default=True,
    help="""Grid size (nrows, ncols).""",
)
@click.option(
    "-n",
    "--n-exp",
    type=int,
    default=1,
    show_default=True,
    help="""Number of exposures per filter and exposure time.""",
)
@click.option(
    "-r",
    "--readout",
    type=int,
    default=0,
    show_default=True,
    help="Readout mode as specified by the camera.",
)
@click.option(
    "-b", "--binning", type=str, default="1x1", show_default=True, help="Binning mode."
)
@click.option(
    "-u",
    "--ut-start",
    type=str,
    help="""UT start time of the observation in the ISOT format. If none
            given, the object will be scheduled for the best possible time.""",
)
@click.option(
    "-c",
    "--comment",
    type=str,
    default="",
    show_default=True,
    help="""Comment to be added to the schedule.""",
)
@click.option(
    "-w",
    "--write",
    type=str,
    default="",
    help="""Write a .sch file with the given name. If none given,
            a name is generated from the observing code.""",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    default=0,
    type=click.IntRange(0, 1),
    help="Increase verbosity",
)
@click.version_option()
def mk_mosaic_schedule_cli(
    source,
    filters,
    exp_times,
    observer,
    overlap=5,
    fov=(20, 20),
    grid_size=(3, 3),
    n_exp=1,
    readout=0,
    binning="1x1",
    ut_start=None,
    comment="",
    write=None,
    verbose=-1,
):
    """Generates an ObservingBlock set or a .sch file for mosaic imaging of wide fields.\b

    This script takes a source name to be resolved by `~astropy.coordinates.SkyCoord.from_name`
    or a pair of ICRS coordinates that initalizes a `~astropy.coordinates.SkyCoord` object and
    generates an `~astroplan.ObservingBlock` set or an .sch file.

    .. hint::

        Tools like `Telescopius <https://telescopius.com/telescope-simulator>`_ can be used to
        help you determine the calculate the `fov` and select the best `grid_size` and
        `overlap` for your particular telescope and target combination.

    Parameters
    ----------
    source : str
        Source name to resolve coordinates or a pair of ICRS ra,dec coordinates

    filters : str or tuple of str
        Filters to use. Multiple filters can be specified by a tuple, e.g. ('b', 'g', 'r')

    exp_times : float or tuple of float
        Exposure times to use. Multiple exposure times can be specified by a tuple, e.g. (10, 20)

    observer : tuple of str
        Observer name and 3-character code, e.g. ('Walter Golay', 'XWG')

    overlap : float, default=5
        Overlap between pointings (arcmin).

    fov : tuple of float, default=(20, 20)
        Field of view (arcmin).

    grid_size : tuple of int, default=(3, 3)
        Grid size (nrows, ncols).

    n_exp : int, default=1
        Number of exposures per filter and exposure time.

    readout : int, default=0
        Readout mode as specified by the camera.

    binning : str, default='1x1'
        Binning mode.

    ut_start : str, optional
        UT start time of the observation in the ISOT format. If none given,
        the object will be scheduled for the best possible time.

    comment : str, optional
        Comment to be added to the schedule.

    write : str, optional
        Write a .sch file with the given name. If none given from the command line,
        a name is generated from the observing code. Otherwise, a file will not
        be written and the ObservingBlock set will be returned.

    verbose : int, {-1, 0, 1}, default=-1
        Verbosity level. 0: no debug messages, 1: debug messages. Default set to -1
        for API use and 0 for CLI use.

    Returns
    -------
    obsblocks : `~astroplan.ObservingBlock` tuple or None
        Set of ObservingBlocks for the mosaic observation.

    Raises
    ------
    `click.BadParameter

    See Also
    --------
    pyscope.telrun.schedtel
    astropy.coordinates.SkyCoord

    Examples
    --------
    API use:

    .. doctest::

        >>> from pyscope.telrun import mk_mosaic_schedule, schedtel
        >>> blocks = mk_mosaic_schedule('M31', 'g', 30, ('Walter Golay', 'XWG'))

    """

    if len(filters) != len(exp_times):
        raise click.BadParameter(
            "Number of filters must match number of exposure times"
        )

    if verbose > -1:
        logger.setLevel(int(10 * (2 - verbose)))
        logger.addHandler(logging.StreamHandler())
    logger.debug(f"Verbosity level set to {verbose}")
    logger.debug(
        f"""mk_mosaic_schedule_cli(source={source}, filters={filters},
        exp_times={exp_times}, observer={observer}, overlap={overlap}, fov={fov},
        grid_size={grid_size}, n_exp={n_exp}, readout={readout}, binning={binning},
        ut_start={ut_start}, comment={comment}, write={write}, verbose={verbose})"""
    )

    if len(source.split(",")) == 2:
        ra, dec = source.split(",")
        center = coord.SkyCoord(ra, dec, unit=("hourangle", "deg"))
    else:
        center = coord.SkyCoord.from_name(source)
    logger.debug(
        f"Resolved coordinates: {center.to_string('hmsdms', sep=':', precision=1)}"
    )

    # Generate grid
    dra = (fov[0] - overlap) / 60 / np.cos(center.dec.deg * np.pi / 180.0)
    ddec = (fov[1] - overlap) / 60
    ra_list = np.linspace(
        center.ra.deg - (grid_size[1] - 1) * dra / 2.0,
        center.ra.deg + (grid_size[1] - 1) * dra / 2.0,
        grid_size[1],
        endpoint=True,
    )
    dec_list = np.linspace(
        center.dec.deg - (grid_size[0] - 1) * ddec / 2.0,
        center.dec.deg + (grid_size[0] - 1) * ddec / 2.0,
        grid_size[0],
        endpoint=True,
    )
    grid_list = np.array(np.meshgrid(ra_list, dec_list)).T.reshape(-1, 2)

    # Generate ObservingBlocks
    obsblocks = []
    for i, pos in enumerate(grid_list):
        for j in range(len(filters)):
            filt = filters[j]
            exp = exposures[j]
            constraints = None

            if utstart is not None:
                constraints = [
                    [
                        astroplan.constraints.TimeConstraint(
                            utstart + (j + k * len(j)) * exp * u.second - schederr,
                            utstart + (j + k * len(j)) * exp * u.second + schederr,
                        )
                    ]
                    for k in range(n_exp)
                ]

            for j in range(n_exp):
                obsblocks.append(
                    astroplan.ObservingBlock(
                        astroplan.FixedTarget(
                            coord.SkyCoord(pos[0], pos[1], unit="deg")
                        ),
                        exp_times[j],
                        priority=1,
                        configuration={
                            "observer": observer[0],
                            "code": observer[1],
                            "title": f"Mosaic imaging of {source}",
                            "filter": filters[j],
                            "exposure": exp_times[j],
                            "n_exp": 1,
                            "readout": readout,
                            "binning": binning.split("x"),
                            "comment": comment,
                        },
                        constraints=constraints[j] if constraints is not None else None,
                        name=f"{source}_{i}_{j}",
                    )
                )
                logger.debug(
                    f"""Created ObservingBlock: {blocks[-1].target},
                    {blocks[-1].duration}, {blocks[-1].priority},
                    {blocks[-1].name}, {blocks[-1].constraints},
                    {blocks[-1].configuration}"""
                )

    if write is not None:
        if write == "":
            write = f"{observer[1]}{strftime('%j', localtime())}.sch"
        with open(write, "w") as f:
            f.write(f"tit 'Mosaic imaging of {source}'\n")
            f.write(f"obs '{observer[0]}'\n")
            f.write("# Schedule generated by mk-mosaic-sched'\n")
            f.write(f"filt {','.join(filters)} exp {','.join(exp_times)}\n\n")
            for block in obsblocks:
                ra_str, dec_str = block.target.to_string(
                    style="hmsdms",
                    precision=3,
                    sep=":",
                    decimal=True,
                ).split()
                f.write(
                    f"""sou {block.name} ra {ra_str} dec {dec_str} repe {n_exp} uts {utstart} rea {readout} bin {binning} com {comment}\n"""
                )

    if verbose > -1:
        logger.info("============================================================")
        logger.info("Mosaic of %s" % source)
        logger.info(
            "%i filters, %.0f minutes per filter sequence"
            % (len(filters), sum(exp_times))
        )
        logger.info("Repeat each filter sequence %i times" % n_exp)
        logger.info(
            "%i x %i field, %i fields total"
            % (grid_size[0], grid_size[1], grid_size[0] * grid_size[1])
        )
        logger.info(
            "%i images, total observing time %0.1f hours"
            % (len(obsblocks), len(filters) * sum(exp_times) * n_exp / 3600.0)
        )
        logger.info("Output file: %s" % write)
        logger.info("============================================================")


mk_mosaic_schedule = mk_mosaic_schedule_cli.callback
