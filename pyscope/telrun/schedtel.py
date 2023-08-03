import configparser
import datetime
import json
import logging
import os
import pytz
import shlex

import astroplan
from astropy import coordinates as coord, time as astrotime, units as u
from astroquery import mpc
import click
import cmcrameri as ccm
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib import ticker
import smplotlib
import timezonefinder

from .. import utils
from ..observatory import Observatory

logger = logging.getLogger(__name__)

@click.command()
@click.option('-c', '--catalog', type=click.Path(resolve_path=True),
              default='schedules/schedule.cat', show_default=True,
              help='A path to a .cat file containing a list of .sch files, a single .sch file, or a list of ObservingBlocks to be scheduled.')
@click.option('-i', '--ignore-order', 'ignore_order', is_flag=True, default=False, show_default=True,
              help='Ignore the order of the .sch files in the catalog, acting as if there is only one .sch file. By default, the .sch files are scheduled one at a time.')
@click.option('-d',
              '--date',
              type=click.DateTime(formats=['%m-%d-%Y']),
              default=None,
              show_default=False,
              help='The local date at the observatory of the night to be scheduled. By default, the current date at the observatory location is used.')
@click.option('-o', '--observatory', type=click.Path(resolve_path=True),
              default='./config/observatory.cfg', show_default=True,
              help=('The configuration file of the observatory that will execute this schedule'))
@click.option('-m', '--max-altitude', 'max_altitude', type=click.FloatRange(max=90), default=-12, show_default=True,
              help='The maximum altitude of the Sun for the night [degrees]. Civil twilight is -6, nautical twilight is -12, and astronomical twilight is -18.')
@click.option('-e',
              '--elevation',
              type=click.FloatRange(min=0,
                                    max=90,
                                    clamp=True),
              default=30,
              show_default=True,
              help='The minimum elevation of all targets [degrees]. This is a "boolean" constraint; that is, there is no understanding of where it is closer to ideal to observe the target. To implement a preference for higher elevation targets, the airmass constraint should be used.')
@click.option('-a', '--airmass', type=click.FloatRange(min=1), default=3, show_default=True,
              help='The maximum airmass of all targets. If not specified, the airmass is not constrained.')
@click.option('-c', '--moon-separation', type=click.FloatRange(min=0), default=30, show_default=True,
                help='The minimum angular separation between the Moon and all targets [degrees].')
@click.option('-s', '--scheduler', nargs=2, type=(click.Path(exists=True, resolve_path=True), str), default=('', ''), show_default=False,
              help=('The filepath to and name of an astroplan.Scheduler custom sub-class. By default, the astroplan.PriorityScheduler is used.'))
@click.option('-g', '--gap-time', 'gap_time', type=click.FloatRange(min=0), default=60, show_default=True,
              help='The maximumum length of time a transition between ObservingBlocks could take [seconds].')
@click.option('-r', '--resolution', type=click.FloatRange(min=0), default=5, show_default=True,
              help='The time resolution of the schedule [seconds].')
@click.option('-f', '--filename', type=click.Path(), default=None, show_default=False,
              help='The output file name. The file name is formatted with the UTC date of the first observation in the schedule. By default, it is placed in the current working directory, but if a path is specified, the file will be placed there. WARNING: If the file already exists, it will be overwritten.')
@click.option('-t', '--telrun', is_flag=True, default=False, show_default=True,
              help='Places the output file in ./schedules/ or in the directory specified by the $TELRUN_EXECUTE environment variable. Causes -f/--filename to be ignored. WARNING: If the file already exists, it will be overwritten.')
@click.option('-p', '--plot', type=click.IntRange(1, 3), default=None, show_default=False,
              help='Plots the schedule. 1: plots the schedule as a Gantt chart. 2: plots the schedule by target with airmass. 3: plots the schedule on a sky chart.')
@click.option('-q', '--quiet', is_flag=True, default=False,
              show_default=True, help='Quiet output')
@click.option('-v', '--verbose', default=0, show_default=True,
              count=True, help='Verbose output')
@click.version_option(version='0.1.0')
@click.help_option('-h', '--help')
def schedtel(catalog, ignore_order, date, observatory, 
            max_altitude, elevation, airmass, 
            moon_separation, scheduler, 
            gap_time, resolution, filename, 
            telrun, plot, quiet, verbose):
    
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

    logger.info('Starting schedtel')
    logger.debug(f'catalog: {catalog}')
    logger.debug(f'ignore_order: {ignore_order}')
    logger.debug(f'date: {date}')
    logger.debug(f'observatory: {observatory}')
    logger.debug(f'max_altitude: {max_altitude}')
    logger.debug(f'elevation: {elevation}')
    logger.debug(f'airmass: {airmass}')
    logger.debug(f'moon_separation: {moon_separation}')
    logger.debug(f'scheduler: {scheduler}')
    logger.debug(f'gap_time: {gap_time}')
    logger.debug(f'resolution: {resolution}')
    logger.debug(f'filename: {filename}')
    logger.debug(f'telrun: {telrun}')
    logger.debug(f'plot: {plot}')
    logger.debug(f'quiet: {quiet}')
    logger.debug(f'verbose: {verbose}')

    blocks = []

    if os.path.isfile(catalog):
        logger.debug(f'catalog is a file')
        if catalog.endswith('.cat'):
            with open(catalog, 'r') as f:
                sch_files = f.read().splitlines()
            for f in sch_files:
                if not os.path.isfile(f):
                    logger.error(f'File {f} in catalog {catalog} does not exist.')
                    return
                blocks.append(parse_sch_file(f))
        elif catalog.endswith('.sch'):
            blocks.append(parse_sch_file(catalog))
    
    elif type(catalog) in (list, tuple, iter):
        logger.debug(f'catalog is a list')
        for block in catalog:
            if type(block) in (list, tuple, iter):
                for b in block:
                    if type(b) is not astroplan.ObservingBlock:
                        logger.error(f'Object {b} in catalog {catalog} is not an astroplan.ObservingBlock.')
                        return
                blocks.append(block)
            elif type(block) is astroplan.ObservingBlock:
                blocks.append([block])
            else:
                logger.error(f'Object {block} in catalog {catalog} is not an astroplan.ObservingBlock.')
                return
    
    if ignore_order:
        blocks = [[blocks[i][j] for i in range(len(blocks)) for j in range(len(blocks[i]))]]

    # Define the observatory
    if type(observatory) is not astroplan.Observer:
        if type(observatory) is str:
            obs_cfg = configparser.ConfigParser()
            obs_cfg.read(observatory)
            obs_long = obs_cfg.getfloat('site', 'longitude')
            obs_lat = obs_cfg.getfloat('site', 'latitude')
            obs_height = obs_cfg.getfloat('site', 'elevation')
            slew_rate = obs_cfg.getfloat('scheduling', 'slew_rate')*u.deg/u.second
            instrument_reconfiguration_times = json.loads(obs_cfg.get('scheduling', 'instrument_reconfiguration_times'))
            instrument_name = obs_cfg.get('site', 'instrument_name')
            observatory = astroplan.Observer(location=coord.EarthLocation(
                lon=obs_long*u.deg, lat=obs_lat*u.deg, height=obs_height*u.m))
        elif type(observatory) is Observatory:
            obs_long = observatory.observatory_location.lon.deg
            obs_lat = observatory.observatory_location.lat.deg
            obs_height = observatory.observatory_location.height.m
            slew_rate = observatory.slew_rate*u.deg/u.second
            instrument_reconfiguration_times = observatory.instrument_reconfiguration_times
            instrument_name = observatory.instrument_name
            observatory = astroplan.Observer(location=observatory.observatory_location)
        else:
            raise TypeError('Observatory must be, a string, Observatory object, or astroplan.Observer object.')
    
    # Constraints
    global_constraints = [
        astroplan.AltitudeConstraint(min=elevation*u.deg),
        astroplan.AtNightConstraint(max_solar_altitude=max_altitude*u.deg),
        astroplan.AirmassConstraint(max=airmass, boolean_constraint=False),
        astroplan.MoonSeparationConstraint(min=moon_separation*u.deg)
        ]

    # Transitioner
    transitioner = astroplan.Transitioner(
        slew_rate,
        instrument_reconfiguration_times=instrument_reconfiguration_times)

    # Schedule
    if date is None:
        tz = timezonefinder.TimezoneFinder().timezone_at(lng=obs_long, lat=obs_lat)
        date = datetime.datetime.now(pytz.timezone(tz))

    t0 = (astrotime.Time(datetime.datetime(date.year, date.month, date.day, 12, 0, 0), 
            format='datetime', scale='utc') 
            - ((astrotime.Time(date, format='datetime', scale='utc') - astrotime.Time.now()).day % 1)*u.day)
    t1 = t0 + 1*u.day

    schedule = astroplan.Schedule(t0, t1)

    # Scheduler
    if scheduler[0] == '':
        schedule_handler = astroplan.PriorityScheduler(constraints=global_constraints,
            observer=observatory,
            transitioner=transitioner,
            gap_time=gap_time*u.second,
            time_resolution=time_resolution*u.second)
    else:
        spec = importlib.util.spec_from_file_location(scheduler[0].split('/')[-1].split('.')[0], scheduler[0])
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        schedule_handler_class = getattr(module, scheduler[1])
        if not astroplan.Scheduler in schedule_handler_class.__bases__:
            logger.error(f'Scheduler {scheduler[0]} does not inherit from astroplan.Scheduler.')
            return
        schedule_handler = schedule_handler_class(constraints=global_constraints,
            observer=observatory,
            transitioner=transitioner,
            gap_time=gap_time*u.second,
            time_resolution=time_resolution*u.second)
    
    for block in blocks:
        schedule_handler(blocks, schedule)

    # Generate schedule table
    schedule_table = schedule.to_table(show_transitions=False, show_unused=False)
    
    # Re-assign filenames
    name_dict = {}
    for i in range(len(schedule_table)):
        name = schedule_table[i]['configuration']['obscode']

        if name in name_dict:
            name_dict[name] += 1
        else:
            name_dict[name] = 0

        name += ('%3.3g' % date.strftime('%j')) + '_' + ('%4.4g' % name_dict[name]) + '.fts'
        schedule_table[i]['configuration']['filename'] = name

    # Write the telrun.ecsv file
    if filename is None or telrun:
        first_time = astrotime.Time(schedule_table[0]['start time (UTC)'], format='iso', scale='utc').strftime('%m-%d-%Y')
        filename = 'telrun_' + first_time + '.ecsv'
    
    if telrun:
        try:
            path = os.environ.get('TELRUN_EXECUTE')
        except:
            path = os.getcwd() + '/schedules/'
        if not os.path.isdir(path):
            raise FileNotFoundError(f'Path {path} does not exist.')
    else:
        path = os.getcwd() + '/'
    schedule_table.write(path+filename, format='ascii.ecsv', overwrite=True)

    # Plot the schedule
    ax = None
    match plot:
        case 1: # Gantt chart
            ax = plot_schedule_gantt(schedule, observatory, name=instrument_name)
            return schedule_table, ax
        case 2: # Plot by target w/ altitude
            ax = astroplan.plots.plot_schedule_airmass(schedule)
            plt.legend()
            return schedule_table, ax
        case 3: # Sky chart
            objects = []; times = []
            for i in range(len(schedule_table)):
                if schedule_table[i]['ra'] not in [obj.ra.dms for obj in objects]:
                    objects.append(coord.SkyCoord(ra=schedule_table[i]['ra'], dec=schedule_table[i]['dec']))
                    times.append([(astrotime.Time(schedule_table[i]['start time (UTC)'], format='iso', scale='utc')
                    +astrotime.Time(schedule_table[i]['end time (UTC)'], format='iso', scale='utc'))/2])
                elif schedule_table[i]['dec'] != [obj.ra.dms for obj in objects].index(schedule_table[i]['ra']):
                    objects.append(coord.SkyCoord(ra=schedule_table[i]['ra'], dec=schedule_table[i]['dec']))
                    times.append([(astrotime.Time(schedule_table[i]['start time (UTC)'], format='iso', scale='utc')
                    +astrotime.Time(schedule_table[i]['end time (UTC)'], format='iso', scale='utc'))/2])
                else:
                    times[[obj.dec.dms for obj in objects].index(schedule_table[i]['dec'])].append((
                        astrotime.Time(schedule_table[i]['start time (UTC)'], format='iso', scale='utc')
                        +astrotime.Time(schedule_table[i]['end time (UTC)'], format='iso', scale='utc'))/2)
            
            for i in range(len(objects)):
                ax = astroplan.plot_sky(astroplan.FixedTarget(objects[i]), observatory, times[i], 
                                   style_kwargs={'color':ccm.batlow(i/(len(objects)-1)), 
                                                 'label':objects[i].to_string('hmsdms')})
            plt.legend()
            return schedule_table, ax
        case _:
            pass

    return schedule_table

@click.command()
@click.argument('schedule_table', type=click.Path(exists=True), help='Schedule table to plot.')
@click.argument('observatory', type=click.Path(exists=True), help='Observatory configuration file.')
@click.option('-n', '--name', type=str, default='', help='Name of observatory.')
@click.version_option('-v', '--version', version='0.1.0')
@click.help_option('-h', '--help')
def plot_schedule_gantt(schedule_table, observatory, name):

    if type(schedule_table) is not table.Table:
        schedule_table = table.Table.read(schedule_table, format='ascii.ecsv')
    
    if type(observatory) is not astroplan.Observer:
        if type(observatory) is str:
            obs_cfg = configparser.ConfigParser()
            obs_cfg.read(observatory)
            location = coord.EarthLocation(
                lon=obs_cfg.getfloat('location', 'longitude')*u.deg,
                lat=obs_cfg.getfloat('location', 'latitude')*u.deg,
                height=obs_cfg.getfloat('location', 'elevation')*u.m)
            name = obs_cfg.get('site', 'instrument_name')
            observatory = astroplan.Observer(location=location)
        elif type(observatory) is Observatory:
            location = observatory.observatory_location
            name = observatory.instrument_name
            observatory = astroplan.Observer(location=observatory.observatory_location)
        else:
            raise TypeError('Observatory must be, a string, Observatory object, or astroplan.Observer object.')
    else:
        location = observatory.location
        name = observatory.name

    obscodes = np.unique([block['configuration']['obscode'] for block in schedule_table])

    date = astrotime.Time(schedule_table[0]['start time (UTC)'], format='iso', scale='utc').datetime
    t0 = (astrotime.Time(datetime.datetime(date.year, date.month, date.day, 12, 0, 0), 
            format='datetime', scale='utc') 
            - ((astrotime.Time(date, format='datetime', scale='utc') - astrotime.Time.now()).day % 1)*u.day)

    fig, ax = plt.subplots(1, 1, figsize=(12, len(obscodes)/2))
    
    for i in range(len(obscodes)):
        plot_blocks = [block for block in schedule_table if block['configuration']['obscode'] == obscodes[i]]

        for block in plot_blocks:
            start_time = astrotime.Time(block['start time (UTC)'], format='iso', scale='utc')
            end_time = astrotime.Time(block['end time (UTC)'], format='iso', scale='utc')
            length_minutes = int((start_time - end_time).sec/60+1)
            times = start_time + np.linspace(0, length_minutes, length_minutes, endpoint=True)*u.minute
            
            obj = coord.SkyCoord(ra=block['ra'], dec=block['dec']).transform_to(coord.AltAz(obstime=times, location=location))
            airmass = utils.airmass(obj.alt*u.deg)

            ax.scatter(times.datetime, i*np.ones(len(times)), lw=0, marker='s', 
                    c=airmass, cmap=ccm.batlow, vmin=1, vmax=3)
        
            scatter = ax.scatter(times.datetime, len(obscodes)*np.ones(len(times)), lw=0, marker='s',
                    c=airmass, cmap=ccm.batlow, vmin=1, vmax=3)
    
    obscodes.append('All')

    twilight_times = [
        t0,
        astrotime.Time(observatory.sun_set_time(t0, which='next'), scale='utc'),
        astrotime.Time(observatory.twilight_evening_civil(t0, which='next'), scale='utc'),
        astrotime.Time(observatory.twilight_evening_nautical(t0, which='next'), scale='utc'),
        astrotime.Time(observatory.twilight_evening_astronomical(t0, which='next'), scale='utc'),
        astrotime.Time(observatory.twilight_morning_astronomical(t0, which='next'), scale='utc'),
        astrotime.Time(observatory.twilight_morning_nautical(t0, which='next'), scale='utc'),
        astrotime.Time(observatory.twilight_morning_civil(t0, which='next'), scale='utc'),
        astrotime.Time(observatory.sun_rise_time(t0, which='next'), scale='utc'),
        t1]
    opacities = [0.8, 0.6, 0.4, 0.2, 0, 0.2, 0.4, 0.6, 0.8]
    for i in range(len(twilight_times)-1):
        ax.axvspan(twilight_times[i].datetime, twilight_times[i+1].datetime, color='grey', alpha=opacities[i])
    
    ax.set_xlabel('Time beginning %s [UTC]' % (twilight_times[1]-0.5*u.hour).strftime('%m-%d-%Y'))
    ax.set_xlim([(twilight_times[1]-0.5*u.hour).datetime, (twilight_times[-2].datetime+0.5*u.hour).datetime])
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    ax.xaxis.set_minor_formatter(ticks.NullFormatter())
    ax.xaxis.set_minor_locator(mdates.MinuteLocator(interval=15))
    ax.xtick_params(rotation=45)

    ax.set_ylabel('Observer Code')
    ax.set_ylim([len(obscodes)+1.5, 0.5])
    ax.yaxis.set_major_formatter(ticker.FixedFormatter(obscodes))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.yaxis.set_minor_formatter(ticks.NullFormatter())
    ax.yaxis.set_minor_locator(ticker.NullLocator())

    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_yticks([1, 1.5, 2, 2.5, 3])
    cbar.set_label('Airmass', rotation=270, labelpad=20)

    ax.set_title('Observing Schedule for %s on %s' % (name, twilight_times[1]-0.5*u.hour).strftime('%m-%d-%Y'))
    ax.grid()

    return ax

def parse_sch_file(filename, location=None, t0=None):
    with open(filename, 'r') as f:
        raw_lines = f.readlines()
    
    # Remove equal signs, quotes, and blank lines
    lines = []
    for line in raw_lines:
        line = line.replace('=', ' ')
        line = line.replace("`", "'")
        line = line.replace('"', "'")
        line = line.replace("‘", "'")
        line = line.replace("’", "'")
    
    lines = [line.split('#')[0] for line in lines] # Remove comments
    lines = [line.split('!')[0] for line in lines] # Remove comments
    lines = [line.replace('\n', '') for line in lines] # Remove line breaks
    ' '.join(mystring.split()) # Remove multiple spaces, trailing and leading whitespace
    lines = [line for line in lines if line != ''] # Remove empty lines
    lines = [line.lower() for line in lines] # Lower case

    # Look for title, observer keywords
    title = ''
    for line in lines:
        title = _get_keyvalue(line, 'tit', start_line=True)
        if title is not None:
            lines.remove(line)
            break

    observer = ''
    for line in lines:
        val += _get_keyvalue(line, 'obs', start_line=True)
        if val is not None:
            lines.remove(line)
            observer += (val+',')

    code = filename[:3]

    prior_filters = None
    prior_exposures = None

    # Parse each line and place into ObservingBlock
    blocks = []

    for line in lines:

        # Required keywords
        target_name = _get_keyvalue(line, ('tar', 'sou', 'obj', 'nam'))
        ra = _get_keyvalue(line, 'ra')
        dec = _get_keyvalue(line, 'dec')
        nonsidereal = _get_flag(line, 'non')

        if None not in (ra, dec):
            obj = coord.SkyCoord(ra, dec, unit=(u.hourangle, u.deg))
            if target_name is None: 
                target_name = obj.to_string('hmsdms')
            obj = astroplan.FixedTarget(name=nm, coord=obj)
            pm_ra_cosdec = telrun.observing_block_config['pm_ra_cosdec']
            pm_dec = telrun.observing_block_config['pm_dec']
        elif target_name != None and not nonsidereal:
            obj = coord.SkyCoord.from_name(target_name)
            obj = astroplan.FixedTarget(name=target, coord=obj)
            pm_ra_cosdec = telrun.observing_block_config['pm_ra_cosdec']
            pm_dec = telrun.observing_block_config['pm_dec']
        elif target_name != None and nonsidereal:
            ephemerides = mpc.MPC.get_ephemeris(target=target_name, 
                                location=location, 
                                start=t0+0.5*u.day, 
                                number=1,
                                proper_motion='sky')
            ra = ephemerides['RA'][0]
            dec = ephemerides['DEC'][0]
            pm_ra_cosdec = ephemerides['dRA cos(Dec)'][0]*u.arcsec/u.hour
            pm_dec = ephemerides['dDec'][0]*u.arcsec/u.hour
            obj = coord.SkyCoord(ra, dec, pm_ra_cosdec=pm_ra_cosdec, pm_dec=pm_dec)
            obj = astroplan.FixedTarget(name=target_name, coord=obj)
        else:
            pass # TODO: allow for sources with no coordinates, i.e. scheduling darks/flats

        # Get non-iterating, non-inheriting keywords
        name = _get_keyvalue(line, 'file')
        if name is None:
            name = telrun.observing_block_config['filename']
    
        priority = _get_keyvalue(line, 'pri')
        priority = int(priority) if priority is not None else 1

        repositioning = _get_keyvalue(line, 'rep')
        if repositioning is not None:
            repositioning = (int(repositioning.split(',')[0]), int(repositioning.split(',')[1]))
        else:
            repositioning = telrun.observing_block_config['repositioning']
        
        shutter_state = _get_keyvalue(line, 'shu', boolean=True)
        if shutter_state is None:
            shutter_state = telrun.observing_block_config['shutter_state']

        readout = _get_keyvalue(line, 'rea')
        if readout is not None:
            readout = int(readout)
        else:
            readout = telrun.observing_block_config['readout']
        
        binning = _get_keyvalue(line, 'bin')
        if binning is not None:
            binning = (int(binning.split(',')[0]), int(binning.split(',')[1]))
        else:
            binning = telrun.observing_block_config['binning']
        
        frame_position = _get_keyvalue(line, 'frame_p')
        if frame_position is not None:
            frame_position = (int(frame_position.split(',')[0]), int(frame_position.split(',')[1]))
        else:
            frame_position = telrun.observing_block_config['frame_position']
        
        frame_size = _get_keyvalue(line, 'frame_s')
        if frame_size is not None:
            frame_size = (int(frame_size.split(',')[0]), int(frame_size.split(',')[1]))
        else:
            frame_size = telrun.observing_block_config['frame_size']
        
        comment = _get_keyvalue(line, 'com')
        if comment is None:
            comment = telrun.observing_block_config['comment']

        # Get timing keywords
        utstart = _get_keyvalue(line, 'uts', 'sta')
        if utstart is not None:
            utstart = astrotime.Time(utstart, format='isot', scale='utc')

        cadence = _get_keyvalue(line, 'cad')
        if cadence is not None:
            cadence = astrotime.TimeDelta(datetime.time(*[int(c) for c in cadence.split(':')]), format='datetime')

            if utstart is None:
                raise ValueError('Must specify utstart if cadence is specified')

        schederr = _get_keyvalue(line, 'sch')
        if schederr is not None:
            schederr = astrotime.TimeDelta(datetime.time(*[int(s) for s in schederr.split(':')]), format='datetime')
        
        if utstart is None and schederr is not None:
            raise ValueError('Must specify utstart if schederr is specified')
        elif utstart is not None and schederr is None:
            schederr = 60*u.second

        # Get exposure behavior keywords
        n_exp = _get_keyvalue(line, ('n_e', 'nex', 'rep'))
        if n_exp is not None:
            n_exp = int(n_exp)
        else:
            n_exp = telrun.observing_block_config['n_exp']

        do_not_interrupt = _get_flag(line, ('don', 'do_', 'do-'))
        if do_not_interrupt is None:
            do_not_interrupt = telrun.observing_block_config['do_not_interrupt']

        # Get iterating, inheriting keywords
        filters = _get_keyvalue(line, 'filt')
        if filters is not None:
            filters = filters.split(',')
            prior_filters = filters
        elif prior_filters is not None:
            filters = prior_filters
        else:
            filters = telrun.observing_block_config['filters']
            prior_filters = None

        exposures = _get_keyvalue(line, 'exp')
        if exposures is not None:
            exposures = [float(e) for e in exposures.split(',')]
            prior_exposures = exposures
        elif prior_exposures is not None:
            exposures = prior_exposures
        else:
            exposures = telrun.observing_block_config['exposures']
            prior_exposures = None
        
        # Sanity Check 1: matching number of filters and exposures
        if len(filters) != len(exposures) and len(filters) != 0:
            raise ValueError('Number of filters must match number of exposures')
        
        # Sanity Check 2: do_not_interrupt and cadence don't both appear:
        if do_not_interrupt is not None and cadence is not None:
            raise ValueError('Cannot specify do_not_interrupt and cadence simultaneously')

        # Sanity Check 3: if cadence is specified, verify it exceeds exposure time
        # times number of exposures times number of filters
        if cadence is not None:
            if cadence < np.sum(exposures)*n_exp*len(filters):
                raise ValueError('Cadence must be greater than total exposure time')
        
        for i in range(len(filters)):
            filt = filters[i]
            exp = exposures[i]
            constraints = None
            
            if do_not_interrupt:
                loop_max = 1
                temp_dur = exp*n_exp*u.second
                temp_n_exp = n_exp
            else:
                loop_max = n_exp
                temp_dur = exp*u.second
                temp_n_exp = 1

            if utstart is not None:
                if cadence is not None:
                    constraint_cadence = cadence
                else: 
                    constraint_cadence = temp_dur

                constraints = [[astroplan.constraints.TimeConstraint(
                    utstart + (i+j*len(i))*constraint_cadence - schederr, 
                    utstart + (i+j*len(i))*constraint_cadence + schederr)] 
                    for j in range(loop_max)]

            for j in range(loop_max):
                blocks.append(astroplan.ObservingBlock(
                    target=obj, 
                    duration=temp_dur,
                    priority=priority,
                    name=target_name,
                    configuration={
                        'observer': observer,
                        'code': code,
                        'title': title,
                        'filename': name,
                        'filter': filt,
                        'exposure': exp,
                        'n_exp': temp_n_exp,
                        'do_not_interrupt': do_not_interrupt,
                        'repositioning': repositioning,
                        'shutter_state': shutter_state,
                        'readout': readout,
                        'binning': binning,
                        'frame_position': frame_position,
                        'frame_size': frame_size,
                        'pm_ra_cosdec': pm_ra_cosdec,
                        'pm_dec': pm_dec,
                        'comment': comment,
                        'status': 'N',
                        'message':'unprocessed'},
                    constrains=constraints[j]))

    return blocks

def _get_keyvalue(line, keyword, start_line=False, boolean=False):
    if start_line:
        if line.lower().startswith(keyword.lower()):
            if not boolean:
                return shlex.split(line)[1]
            else:
                if shlex.split(line)[1].lower().startswith(('t', 'y', '1')):
                    return True
                elif shlex.split(line)[1].lower().startswith(('f', 'n', '0')):
                    return False
                else:
                    return None
        else:
            return None

    for i in range(len(line)):
        if line[i:].lower().startswith(keyword.lower()):
            return shlex.split(line[i:])[1]
        else:
            return None

def _get_flag(line, keyword):
    for i in range(len(line)):
        if line[i:].lower().startswith(keyword.lower()):
            return True
    
    return False