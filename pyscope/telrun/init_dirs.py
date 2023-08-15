import logging
import os
import platform
import shutil

import click

from .syncfiles import _read_syncfiles_cfg, _get_client, _sync_directory

logger = logging.getLogger(__name__)

@click.command()
@click.argument('path', type=click.Path(resolve_path=True),
                default='./pyscope-observatory/',
                required=False)
@click.version_option(version='0.1.0')
@click.help_option('-h', '--help')
def init_telrun_dir_cli(path):
    '''test'''
    logger.debug(f'init_telrun_dir(path={path})')

    logger.info('Initializing a telrun home directory at %s' % path)

    if os.path.exists(path):
        logger.error(f'Path {path} already exists')
        raise click.Abort()
    
    logger.info(f'Creating directory {path}')
    os.mkdir(path)

    logger.info(f'Creating subdirectories')
    os.mkdir(os.path.join(path, 'config'))
    os.mkdir(os.path.join(path, 'schedules'))
    os.mkdir(os.path.join(path, 'images'))
    os.mkdir(os.path.join(path, 'logs'))

    logger.info('Creating empty config files')
    shutil.copyfile(
        os.path.join(os.path.dirname(__file__),
        '../config/telrun.cfg'), 
        os.path.join(path, 'config/telrun.cfg'))
    
    shutil.copyfile(
        os.path.join(os.path.dirname(__file__),
        '../config/observatory.cfg'), 
        os.path.join(path, 'config/observatory.cfg'))

    logger.info('Copying default shortcut startup script')
    if platform.system() == 'Windows':
        shutil.copyfile(
            os.path.join(os.path.dirname(__file__),
            'start_telrun.bat'), 
            os.path.join(path, 'start_telrun.bat'))
    else:
        shutil.copyfile(
            os.path.join(os.path.dirname(__file__),
            'start_telrun'), 
            os.path.join(path, 'start_telrun'))
    
    logger.info('Done')

@click.command()
@click.argument('path', type=click.Path(resolve_path=True, exists=True),
                default='./pyscope-observatory/',
                required=False)
@click.version_option(version='0.1.0')
@click.help_option('-h', '--help')
def init_remote_dir_cli(path):
    logger.debug(f'init_remote_dir(path={path})')

    logger.info('Initializing a remote telrun home directory from %s' % path)

    if not os.path.exists(os.path.join(path, 'config/syncfiles.cfg')):
        logger.info('No syncfiles.cfg found, creating one' % path)

        shutil.copyfile(
            os.path.join(os.path.dirname(__file__),
            '../config/syncfiles.cfg'), 
            os.path.join(path, 'config/syncfiles.cfg'))
    
        logger.info('Opening text editor... Please complete all fields and save the file')
        if platform.system() == 'Windows':
            os.system(os.path.join(path, 'config/syncfiles.cfg'))
        else:
            try: 
                logger.info('Trying to open $EDITOR')
                os.system('%s %s' % (os.getenv('EDITOR'), os.path.join(path, 'config/syncfiles.cfg')))
            except:
                logger.warning('Could not open $EDITOR, trying to open vi')
                os.system('vi ' + os.path.join(path, 'config/syncfiles.cfg'))
        
        input('Press enter to continue...')
    
    logger.info('Reading syncfiles.cfg')

    local_config_dir = os.path.join(path, 'config')

    (uname, hostname, p, k,
        remote_config_dir,
        local_schedules_dir, remote_schedules_dir, 
        local_images_dir, remote_images_dir,
        local_logs_dir, remote_logs_dir) = _read_syncfiles_cfg(
            os.path.join(local_config_dir, 'syncfiles.cfg'))

    logger.info('Performing initial single sync')

    logger.info('Getting SSH and SCP clients')
    ssh, scp = _get_client(uname, hostname, p, k)

    logger.info('Syncing config directory')
    _sync_directory(scp, local_config_dir, remote_config_dir, 'send', '.cfg')

    logger.info('Syncing schedules directory')
    _sync_directory(scp, local_schedules_dir, remote_schedules_dir, 'both', '.ecsv')

    logger.info('Syncing images directory')
    _sync_directory(scp, local_images_dir, remote_images_dir, 'send', ('.fts', '.fits', '.fit'))

    logger.info('Syncing logs directory')
    _sync_directory(scp, local_logs_dir, remote_logs_dir, 'send', ('.log', '.ecsv'))

    logger.info('Closing SSH and SCP clients')
    ssh.close()

    logger.info('Copying default shortcut startup script')
    if platform.system() == 'Windows':
        shutil.copyfile(
            os.path.join(os.path.dirname(__file__),
            'start_syncfiles.bat'), 
            os.path.join(path, 'start_syncfiles.bat'))
    else:
        shutil.copyfile(
            os.path.join(os.path.dirname(__file__),
            'start_syncfiles'), 
            os.path.join(path, 'start_syncfiles'))

init_telrun_dir = init_telrun_dir_cli.callback
init_remote_dir = init_remote_dir_cli.callback