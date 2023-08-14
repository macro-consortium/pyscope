import atexit
import configparser
import logging
import os
import threading

import click
import paramiko

logger = logging.getLogger(__name__)

@click.command()
@click.option('-c', '--config',
                default='./config/', show_default=True,
                type=click.Path(exists=True, resolve_path=True), 
                help='Path to config directory on local and remote machines')
@click.option('-r', '--remote-config', 'remote_config', type=str,
                help='Path to config directory on remote machine')
@click.option('-u', '--username', type=str, 
                help='Username for remote server')
@click.option('-h', '--host', type=str,
                help='Hostname of remote server')
@click.option('-p', '--port', type=int,
                help='SSH port of remote server')
@click.option('-k', '--key', type=click.Path(exists=True, resolve_path=True),
                help='Path to SSH key file')
@click.option('-s', '--schedules', nargs=2, 
                type=(click.Path(exists=True, resolve_path=True), click.Path()), 
                help='Path to schedules directory on local and remote machines')
@click.option('-i', '--images', nargs=2,
                type=(click.Path(exists=True, resolve_path=True), click.Path()),
                help='Path to images directory on local and remote machines')
@click.option('-l', '--logs', nargs=2,
                type=(click.Path(exists=True, resolve_path=True), click.Path()),
                help='Path to logs directory on local and remote machines')
@click.version_option(version='0.1.0')
@click.help_option('-h', '--help')
def syncfiles(config, remote_config, username, host, port, key, schedules, images, logs):

    logger.info('Starting syncfiles')
    logger.debug(f'syncfiles({username}, {host}, {port}, {key}, {config}, {schedules}, {images}, {logs})')
    
    # Get local and remote config directories
    local_config_dir = config

    if os.path.isfile(local_config_dir):
        logger.info('Local config directory is a file, getting parent directory')
        local_config_dir = os.path.abspath(os.path.dirname(local_config_dir))

    # Get mtime of syncfiles.cfg
    syncfiles_mtime = os.path.getmtime(local_config_dir+'/syncfiles.cfg')

    # Read syncfiles.cfg
    (uname, hostname, p, k, 
    remote_config_dir,
    local_schedules_dir, remote_schedules_dir, 
    local_images_dir, remote_images_dir,
    local_logs_dir, remote_logs_dir) = _read_syncfiles_cfg(
                                    local_config_dir+'/syncfiles.cfg')

    # Override with any arguments passed in
    if remote_config is not None:
        remote_config_dir = remote_config
    if username is not None:
        uname = username
    if host is not None:
        hostname = host
    if port is not None:
        p = port
    if key is not None:
        k = key
    if schedules is not None:
        local_schedules_dir, remote_schedules_dir = schedules
    if images is not None:
        local_images_dir, remote_images_dir = images
    if logs is not None:
        local_logs_dir, remote_logs_dir = logs
    
    # Initial config directory sync
    logger.info('Performing initial config directory sync')
    cfg_ssh, cfg_scp = _get_client(uname, hostname, p, k)
    _sync_directory(cfg_scp, local_config_dir, remote_config_dir, 'send', '.cfg')
    
    # Thread event
    threads_event = threading.Event()

    # Create clients and threads
    logger.info('Creating clients and threads')
    sch_ssh, sch_scp = _get_client(uname, hostname, p, k)
    sch_thread = threading.Thread(target=_continuous_sync, 
        args=(sch_scp,
        local_schedules_dir, remote_schedules_dir, 'both', '.ecsv', 
        threads_event), 
        daemon=True, 
        name='sch_thread')

    img_ssh, img_scp = _get_client(uname, hostname, p, k)
    img_thread = threading.Thread(target=_continuous_sync,
        args=(img_scp,
        local_images_dir, remote_images_dir, 'send', ('.fts', '.fits', '.fit'), 
        threads_event), 
        daemon=True,
        name='img_thread')

    log_ssh, log_scp = _get_client(uname, hostname, p, k)
    log_thread = threading.Thread(target=_continuous_sync,
        args=(log_scp,
        local_logs_dir, remote_logs_dir, 'send', ('.log', '.ecsv'),
        threads_event), 
        daemon=True,
        name='log_thread')

    # Register exit function
    atexit.register(_close_connection, (cfg_ssh, sch_ssh, img_ssh, log_ssh))

    # Start threads
    logger.info('Starting threads')
    sch_thread.start()
    img_thread.start()
    log_thread.start()

    logger.info('Starting loop')
    while True:
        if (os.path.getmtime(local_config_dir+'/syncfiles.cfg') > syncfiles_mtime):
            logger.info('syncfiles.cfg has been modified')

            # Update mtime
            logger.info('Updating mtime')
            syncfiles_mtime = os.path.getmtime(local_config_dir+'/syncfiles.cfg')

            # Stop threads from starting next loop sync and wait for them to finish
            logger.info('Stopping threads')
            threads_event.set()
            sch_thread.join()
            img_thread.join()
            log_thread.join()
            threads_event.clear()

            # End old ssh connections
            logger.info('Closing old connections')
            _close_connection((cfg_ssh, sch_ssh, img_ssh, log_ssh))

            # Re-parse the syncfiles.cfg
            logger.info('Re-parsing syncfiles.cfg')
            (uname, hostname, p, k,
            remote_config_dir,
            local_schedules_dir, remote_schedules_dir, 
            local_images_dir, remote_images_dir,
            local_logs_dir, remote_logs_dir) = _read_syncfiles_cfg(local_config_dir+'/syncfiles.cfg')

            # Sync config directory
            logger.info('Syncing config directory')
            cfg_ssh, cfg_scp = _get_client(uname, hostname, p, k)
            _sync_directory(cfg_scp, local_config_dir, remote_config_dir, 'send', '.cfg')

            # Create clients and threads
            logger.info('Creating clients and threads')
            sch_ssh, sch_scp = _get_client(uname, hostname, p, k)
            sch_thread = threading.Thread(target=_continuous_sync, 
                args=(sch_scp,
                local_schedules_dir, remote_schedules_dir, 'both', '.ecsv', 
                threads_event), 
                daemon=True, 
                name='sch_thread')

            img_ssh, img_scp = _get_client(uname, hostname, p, k)
            img_thread = threading.Thread(target=_continuous_sync,
                args=(img_scp,
                local_images_dir, remote_images_dir, 'send', ('.fts', '.fits', '.fit'), 
                threads_event), 
                daemon=True,
                name='img_thread')

            log_ssh, log_scp = _get_client(uname, hostname, p, k)
            log_thread = threading.Thread(target=_continuous_sync,
                args=(log_scp,
                local_logs_dir, remote_logs_dir, 'send', ('.log', '.ecsv'),
                threads_event), 
                daemon=True,
                name='log_thread')
            
            # Register exit function
            atexit.register(_close_connection, (cfg_ssh, sch_ssh, img_ssh, log_ssh))

            # Start threads
            logger.info('Starting threads')
            sch_thread.start()
            img_thread.start()
            log_thread.start()

        else:
            logger.debug('syncfiles.cfg has not been modified')
            _sync_directory(cfg_scp, local_config_dir, remote_config_dir, 'send', '.cfg') # Sync config directory
            time.sleep(1) # Sleep for 1 second

def _read_syncfiles_cfg(syncfiles_cfg):
    cfg = configparser.ConfigParser()
    cfg.read(syncfiles_cfg)

    uname = cfg.get('DEFAULT', 'username', fallback='telrun')
    hostname = cfg['DEFAULT']['hostname']
    p = cfg.getint('DEFAULT', 'port', fallback=22)
    k = cfg.get('DEFAULT', 'key', fallback='./config/id_rsa')

    remote_config_dir = cfg.get('DEFAULT', 'remote_config_dir', fallback='/home/telrun/config/')
    local_schedules_dir = cfg.get('DEFAULT', 'local_schedules_dir', fallback='./schedules/')
    remote_schedules_dir = cfg.get('DEFAULT', 'remote_schedules_dir', fallback='/home/telrun/schedules/')
    local_images_dir = cfg.get('DEFAULT', 'local_images_dir', fallback='./images/')
    remote_images_dir = cfg.get('DEFAULT', 'remote_images_dir', fallback='/home/telrun/images/')
    local_logs_dir = cfg.get('DEFAULT', 'local_logs_dir', fallback='./logs/')
    remote_logs_dir = cfg.get('DEFAULT', 'remote_logs_dir', fallback='/home/telrun/logs/')

    return (uname, hostname, p, k,
            remote_config_dir,
            local_schedules_dir, remote_schedules_dir, 
            local_images_dir, remote_images_dir,
            local_logs_dir, remote_logs_dir)

def _get_client(username, host, port, key):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port, username, key_filename=key)
    scp = ssh.open_sftp()
    return (ssh, scp)

def _continuous_sync(scp, local_dir, remote_dir, mode, ext, event):
    while not event.is_set():
        _sync_directory(scp, local_dir, remote_dir, mode, ext)
        time.sleep(1)

def _sync_directory(scp, local_dir, remote_dir, mode, ext):
    scp.chdir(remote_dir)
    if mode == 'send':
        for f in os.listdir(local_dir):
            if not f.endswith(ext):
                continue
            if f in scp.listdir():
                if scp.stat(f).st_mtime < os.path.getmtime(local_dir+f):
                    logger.info('Putting local path %s to remote path %s', local_dir+f, remote_dir+f)
                    scp.put(local_dir+f, f)
            else:
                scp.put(local_dir+f, f)
    elif mode == 'receive':
        for f in scp.listdir():
            if not f.endswith(ext):
                continue
            if f in os.listdir(local_dir):
                if scp.stat(f).st_mtime < os.path.getmtime(local_dir+f):
                    logger.info('Getting remote path %s to local path %s', remote_dir+f, local_dir+f)
                    scp.get(f, local_dir+f)
            else:
                scp.get(f, local_dir+f)

def _close_connection(sshs):
    for s in sshs:
        s.close()