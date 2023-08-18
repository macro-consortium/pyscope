import logging

import click
import numpy as np

from .. import reduction
from .observatory import Observatory

logger = logging.getLogger(__name__)

'''
TODO:
- filter-exposures and filter-brightness should be able to handle a single value and apply to all filters
- add option to specify which filters to use
- add option to place masters in a different folder + syncfiles recognition of a directory beginning with master_
- cmos-calib/ccd-calib recognition of most recent directory with master_ prefix
- observatory calibration script improvements
'''

@click.command(epilog='''Check out the documentation at
                https://pyscope.readthedocs.io/ for more
                information.''')
@click.option('-o', '--observatory', type=click.Path(exists=True),
    default='./config/observatory.cfg', show_default=True,
    help='Path to observatory configuration file.')
@click.option('-c', '--camera', type=click.Choice(['ccd', 'cmos']), default='ccd',
    show_default=True, help='Camera type.')
@click.option('-d', '--dark-exposures', type=float, multiple=True, default=[0.1, 1, 10, 100], 
    show_default=True, help='Dark exposure times.')
@click.option('-f', '--filter-exposures', type=float, multiple=True, 
    help='The flat exposure times for each filter.')
@click.option('-i', '--filter-brightness', type=float, multiple=True,
    help='The intensity of the calibrator [if present] for each filter.')
@click.option('-r', '--readouts', type=int, multiple=True, default=[0],
    show_default=True, help='Readout modes to iterate through.')
@click.option('-b', '--binnings', type=str, multiple=True, default=['1x1'],
    show_default=True, help='Binnings to iterate through.')
@click.option('-n', '--repeat', type=int, default=10, show_default=True,
    help='Number of times to repeat each exposure.')
@click.option('-s', '--save-path', type=click.Path(exists=True), default='./images/',
    show_default=True, help='Path to save calibration set.')
@click.option('-m', '--mode', type=click.Choice(['0', '1']), default=0, show_default=True,
    help='Mode to use for averaging FITS files (0 = median, 1 = mean).')
@click.version_option(version='0.1.0')
@click.help_option('-h', '--help')
def collect_calibration_set_cli(observatory,
                                camera,
                                dark_exposures,
                                filter_exposures,
                                filter_brightness,
                                readouts=0, 
                                binnings='1x1', 
                                repeat=10,
                                save_path='./',
                                mode=0):
    
    if type(observatory) == str:
        logger.info(f'Collecting calibration set for {observatory}')
        obs = Observatory(observatory)
    elif type(observatory) == Observatory:
        logger.info(f'Collecting calibration set for {observatory.name}')
        obs = observatory
    else:
        logger.exception(f'Invalid observatory type: {type(observatory)}')
        return False
    
    if type(binnings) == str:
        binnings = binnings.split(',')
    binnings = [tuple(map(int, b.split('x'))) for b in binnings]

    obs.connect_all()

    save_folder = os.path.join(save_path, 
        'calibration_set_%s' % obs.observatory_time().strftime('%Y%-m-%d_%H-%M-%S'))
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    logger.info(f'Saving calibration set to {save_folder}')

    logger.info('Collecting flats')
    success = obs.take_flats(filter_exposures, filter_brightness=filter_brightness,
                   readouts=readouts, binnings=binnings, repeat=repeat,
                   save_path=save_folder, new_folder='flats')
    if not success:
        logger.error('Failed to collect flats')
        return False
    
    if camera == 'cmos':
        logger.info('Collecting flat-darks')
        success = obs.take_darks(np.unique(filter_exposures), readouts=readouts,
                        binnings=binnings, repeat=repeat, save_path=save_folder,
                        new_folder='flat_darks')
        if not success:
            logger.error('Failed to collect flat-darks')
            return False
    
    logger.info('Collecting darks')
    success = obs.take_darks(dark_exposures, readouts=readouts,
                    binnings=binnings, repeat=repeat, save_path=save_folder,
                    new_folder='darks')
    if not success:
        logger.error('Failed to collect darks')
        return False
    
    if camera == 'ccd':
        logger.info('Collecting biases')
        success = obs.take_darks([0], readouts=readouts,
                        binnings=binnings, repeat=repeat, save_path=save_folder,
                        new_folder='biases')
        if not success:
            logger.error('Failed to collect biases')
            return False
    elif camera == 'cmos':
        logger.warning('Skipping bias collection for CMOS camera')
    
    logger.info('Collection complete.')

    logger.info('Creating master directory...')
    os.makedirs(os.path.join(save_folder, 'masters'))
    
    for readout in readouts:
        logger.debug('Readout: %s' % readout)
        for binning in binnings:
            logger.debug('Binning: %ix%i' % (binning[0], binning[1]))
            logger.info('Creating master darks...')
            for exposure in dark_exposures:
                dark_paths = []
                for i in range(repeat):
                    dark_paths.append(os.path.join(os.path.join(save_folder, 'darks'), 
                        ('dark_%s_%ix%i_%4.4gs__%i.fts' % (
                        readout,
                        binning[0], binning[1], 
                        exposure, i))))
                
                reduction.avg_fits(mode=mode, 
                    outfile=os.path.join(os.path.join(save_folder, 'masters'), 
                    ('master_dark_%s_%ix%i_%4.4gs.fts' % (
                    readout,
                    binning[0], binning[1], 
                    exposure))), fnames=dark_paths)

            if camera == 'ccd':
                logger.info('Creating master biases...')
                bias_paths = []
                for i in range(repeat):
                    bias_paths.append(os.path.join(os.path.join(save_folder, 'biases'), 
                        ('bias_%s_%ix%i__%i.fts' % (
                        readout,
                        binning[0], binning[1], 
                        i))))
                
                reduction.avg_fits(mode=mode,
                    outfile=os.path.join(os.path.join(save_folder, 'masters'), 
                    ('master_bias_%s_%ix%i.fts' % (
                    readout,
                    binning[0], binning[1]))), fnames=bias_paths)
            
            logger.info('Creating master flats...')
            for exposure in filter_exposures:
                flat_paths = []
                for i in range(repeat):
                    flat_paths.append(os.path.join(os.path.join(save_folder, 'flats'), 
                        ('flat_%s_%s_%ix%i_%4.4gs__%i.fts' % (
                        filt, readout,
                        binning[0], binning[1], 
                        exposure, i))))
                    
                reduction.avg_fits(mode=mode,
                    outfile=os.path.join(os.path.join(save_folder, 'masters'), 
                    ('master_flat_%s_%ix%i_%4.4gs.fts' % (
                    readout,
                    binning[0], binning[1], 
                    exposure))), fnames=flat_paths)
                
                if camera == 'cmos':
                    logger.info('CMOS camera selected, creating master flat-dark...')
                    flat_dark_paths = []
                    for i in range(repeat):
                        flat_dark_paths.append(os.path.join(os.path.join(save_folder, 'flat_darks'), 
                            ('dark_%s_%ix%i_%4.4gs__%i.fts' % (
                            readout,
                            binning[0], binning[1], 
                            exposure, i))))
                    
                    reduction.avg_fits(mode=mode,
                        outfile=os.path.join(os.path.join(save_folder, 'masters'), 
                        ('master_flat_dark_%s_%ix%i_%4.4gs.fts' % (
                        readout,
                        binning[0], binning[1], 
                        exposure))), fnames=flat_dark_paths)

    logger.info('Calibration set complete.')

collect_calibration_set = collect_calibration_set_cli.callback