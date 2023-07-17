import atexit
import configparser
import os
import shutil

from pyscope import Observatory, logger

def setup_telrun_observatory(telhome):
    pass

class TelrunOperator:
    def __init__(self, config_file_path=None, gui=False, **kwargs):

        # Non-accessible variables
        self._config = configparser.ConfigParser()
        self._gui = None
        self._telrun_file = None
        
        # Read-only variables
        self._telhome = None
        self._observatory = None
        self._dome_type = None # None, 'dome' or 'roll-off'/'clamshell'

        # Read/write variables
        self._wait_for_sun = True
        self._max_solar_elev = -12
        self._wait_for_cooldown = True
        self._autofocus_interval = 3600
        self._initial_autofocus = True
        self._initial_home = True
        self._wait_for_scan_start_time = True
        self._max_scan_late_time = 60
        self._preslew_time = 60
        self._check_safety_monitors = True
        self._hardware_timeout = 60
        self._autofocus_timeout = 180
        self._wcs_timeout = 30

        # Load config file if there
        if config_file_path is not None:
            logger.info('Using config file to initialize telrun: %s' % config_file_path)
            try: self._config.read(config_file_path)
            except: raise TelrunError('Could not read config file: %s' % config_file_path)

            self._telhome = os.path.abspath(os.path.dirname(config_file_path) + '/../')
            self._observatory = self._config.get('observatory')
            self._dome_type = self._config.get('dome_type')
            self._autofocus_interval = self._config.getint('autofocus_interval')
            self._initial_autofocus = self._config.getboolean('initial_autofocus')
            self._initial_home = self._config.getboolean('initial_home')
            self._wait_for_scan_start_time = self._config.getboolean('wait_for_scan_start_time')
            self._wait_for_sun = self._config.getboolean('wait_for_sun')
            self._max_solar_elev = self._config.getfloat('max_solar_elev')
            self._check_safety_monitors = self._config.getboolean('check_safety_monitors')
            self._max_scan_late_time = self._config.getint('max_scan_late_time')
            self._preslew_time = self._config.getint('preslew_time')
            self._hardware_timeout = self._config.getint('hardware_timeout')
            self._autofocus_timeout = self._config.getint('autofocus_timeout')
            self._wcs_timeout = self._config.getint('wcs_timeout')

        # Override config file with kwargs if specified
        self._telhome = kwargs.get('telhome', self._telhome)
        self._observatory = kwargs.get('observatory', self._observatory)
        self._dome_type = kwargs.get('dome_type', self._dome_type)
        self._autofocus_interval = kwargs.get('autofocus_interval', self._autofocus_interval)
        self._initial_autofocus = kwargs.get('initial_autofocus', self._initial_autofocus)
        self._initial_home = kwargs.get('initial_home', self._initial_home)
        self._wait_for_scan_start_time = kwargs.get('wait_for_scan_start_time', self._wait_for_scan_start_time)
        self._wait_for_sun = kwargs.get('wait_for_sun', self._wait_for_sun)
        self._max_solar_elev = kwargs.get('max_solar_elev', self._max_solar_elev)
        self._check_safety_monitors = kwargs.get('check_safety_monitors', self._check_safety_monitors)
        self._max_scan_late_time = kwargs.get('max_scan_late_time', self._max_scan_late_time)
        self._preslew_time = kwargs.get('preslew_time', self._preslew_time)
        self._hardware_timeout = kwargs.get('hardware_timeout', self._hardware_timeout)
        self._autofocus_timeout = kwargs.get('autofocus_timeout', self._autofocus_timeout)

        # Parse telhome
        if self._telhome is None:
            self._telhome = os.path.abspath(os.getcwd())
        setup_telrun_observatory(self._telhome)

        # Initialize observatory
        if self._observatory is None:
            raise TelrunError('observatory must be specified')
        elif type(self._observatory) is str:
            self._observatory = Observatory(config_file_path=self._observatory)
        elif type(self._observatory) is not Observatory:
            raise TelrunError('observatory must be a string representing a config file path \
                or an Observatory object')
        
        # Register shutdown with atexit
        logger.debug('Registering observatory shutdown with atexit')
        atexit.register(self.observatory.shutdown())
        logger.debug('Registered')

        # Open GUI if requested
        if gui:
            logger.info('Starting GUI')
            self._gui = TelrunGUI(self)
            logger.info('GUI started')

        # Connect to observatory hardware
        logger.info('Attempting to connect to observatory hardware')
        self.observatory.connect_all()
        logger.info('Connected')

    def run(self):
        logger.info('Checking for an existing telrun.sls file')
        if os.path.isfile(self.telhome + '/schedules/telrun.sls'):
            logger.info('Loading existing telrun.sls')
            self._telrun_file = TelrunFile(self.telhome + '/schedules/telrun.sls')

        logger.info('Starting main operation loop...')
        while True:
            self._telrun_file = self._main_operation_loop()
    
    def _main_operation_loop(self):
        if os.path.isfile(self.telhome + '/schedules/telrun.new'):
            logger.info('Found telrun.new; renaming to telrun.sls')
            shutil.move(self.telhome + '/schedules/telrun.new', self.telhome + '/schedules/telrun.sls')
            logger.info('Loading telrun.sls')
            self._telrun_file = TelrunFile(self.telhome + '/schedules/telrun.sls')

        if self._telrun_file is None:
            logger.debug('No active telrun file, sleeping...')
            time.sleep(10)
            return

        # Wait for sunset?
        while self.observatory.sun_altaz()[0] > self.max_solar_elev and self.wait_for_sun:
            logger.info('Sun altitude: %.3f degs (above limit of %s)' % (
                self.observatory.sun_altaz()[0], self.max_solar_elev))
            time.sleep(60)
        logger.info('Sun altitude: %.3f degs (below limit of %s), continuing...' % (
            self.observatory.sun_altaz()[0], self.max_solar_elev))

        # Either open dome or check if open
        match self._dome_type:
            case 'dome':
                if self.observatory.dome is not None: 
                    if self.observatory.dome.CanSetShutter:
                        logger.info('Opening the dome shutter...')
                        self.observatory.dome.OpenShutter()
                        logger.info('Opened.')
                    if self.observatory.dome.CanFindHome:
                        logger.info('Finding the dome home...')
                        self.observatory.dome.FindHome()
                        logger.info('Found.')
            case 'safety-monitor' | 'safety_monitor' | 'safetymonitor' | 'safety monitor':
                logger.info('Designating first safety monitor state as dome...')
                if self.observatory.safety_monitor is not None:
                    status = False
                    while not status:
                        if self.observatory.safety_monitor is not (iter, tuple, list):
                            status = self.observatory.safety_monitor.IsSafe
                        else:
                            status = self.observatory.safety_monitor[0].IsSafe
                        logger.info('Safety monitor status: %s' % status)
                        logger.info('Waiting for safety monitor to be safe...')
                        time.sleep(10)
                    logger.info('Safety monitor indicates safe, continuing...')
        
        # Wait for cooler?
        while (self.observatory.camera.CCDTemperature > 
                self.observatory.cooler_setpoint + self.observatory.cooler_tolerance
                and self._wait_for_cooldown):
            logger.info('CCD temperature: %.3f degs (above limit of %.3f with %.3f tolerance)' % (
                self.observatory.camera.CCDTemperature(),
                self.observatory.cooler_setpoint, 
                self.observatory.cooler_tolerance))
            time.sleep(10)
        logger.info('CCD temperature: %.3f degs (below limit of %.3f with %.3f tolerance), continuing...' % (
            self.observatory.camera.CCDTemperature(),
            self.observatory.cooler_setpoint,
            self.observatory.cooler_tolerance))
        
        telrun_file_finished = self._run_scans()

        if telrun_file_finished:
            logger.info('Finished processing all scans in telrun file')

            logger.info('Shutting down observatory')
            self.observatory.shutdown()
            logger.info('Observatory shut down')

            return
        else:
            logger.info('run_scans returned False, new telrun file found!')
            return
    
    def _run_scans(self):
        pass

        '''if self.check_safety_monitors:
            logger.info('Checking safety monitor statuses')

            status = True
            if type(self.observatory.safety_monitor) not in (iter, list, tuple):
                status = self.observatory.safety_monitor.IsSafe()
            else:
                for monitor in self.observatory.safety_monitor:
                    status = status and monitor.IsSafe()
            
            if not status:'''

    def save_config(self, filename):
        save_dir = self.telhome + '/config/'
        self.observatory.save_config(save_dir+'observatory.cfg')
        self._config['observatory'] = save_dir+'observatory.cfg'
        with open(save_dir + filename, 'w') as config_file:
            self._config.write(config_file)
    
    @property
    def telhome(self):
        return self._telhome

    @property
    def observatory(self):
        return self._observatory
    
    @property
    def dome_type(self):
        return self._dome_type

    @property
    def wait_for_sun(self):
        return self._wait_for_sun
    @wait_for_sun.setter
    def wait_for_sun(self, value):
        self._wait_for_sun = bool(value)
        self._config['wait_for_sun'] = str(value)

    @property
    def max_solar_elev(self):
        return self._max_solar_elev
    @max_solar_elev.setter
    def max_solar_elev(self, value):
        self._max_solar_elev = float(value)
        self._config['max_solar_elev'] = str(value)
    
    @property
    def _wait_for_cooldown(self):
        return self._wait_for_cooldown
    @_wait_for_cooldown.setter
    def _wait_for_cooldown(self, value):
        self._wait_for_cooldown = bool(value)
        self._config['wait_for_cooldown'] = str(value)
    
    @property
    def autofocus_interval(self):
        return self._autofocus_interval
    @autofocus_interval.setter
    def autofocus_interval(self, value):
        self._autofocus_interval = float(value)
        self._config['autofocus_interval'] = str(value)

    @property
    def initial_autofocus(self):
        return self._initial_autofocus
    @initial_autofocus.setter
    def initial_autofocus(self, value):
        self._initial_autofocus = bool(value)
        self._config['initial_autofocus'] = str(value)

    @property
    def initial_home(self):
        return self._initial_home
    @initial_home.setter
    def initial_home(self, value):
        self._initial_home = bool(value)
        self._config['initial_home'] = str(value)

    @property
    def wait_for_scan_start_time(self):
        return self._wait_for_scan_start_time
    @wait_for_scan_start_time.setter
    def wait_for_scan_start_time(self, value):
        self._wait_for_scan_start_time = bool(value)
        self._config['wait_for_scan_start_time'] = str(value)

    @property
    def max_scan_late_time(self):
        return self._max_scan_late_time
    @max_scan_late_time.setter
    def max_scan_late_time(self, value):
        self._max_scan_late_time = float(value)
        self._config['max_scan_late_time'] = str(value)

    @property
    def preslew_time(self):
        return self._preslew_time
    @preslew_time.setter
    def preslew_time(self, value):
        self._preslew_time = float(value)
        self._config['preslew_time'] = str(value)

    @property
    def check_safety_monitors(self):
        return self._check_safety_monitors
    @check_safety_monitors.setter
    def check_safety_monitors(self, value):
        self._check_safety_monitors = bool(value)
        self._config['check_safety_monitors'] = str(value)

    @property
    def hardware_timeout(self):
        return self._hardware_timeout
    @hardware_timeout.setter
    def hardware_timeout(self, value):
        self._hardware_timeout = float(value)
        self._config['hardware_timeout'] = str(value)

    @property
    def autofocus_timeout(self):
        return self._autofocus_timeout
    @autofocus_timeout.setter
    def autofocus_timeout(self, value):
        self._autofocus_timeout = float(value)
        self._config['autofocus_timeout'] = str(value)

    @property
    def wcs_timeout(self):
        return self._wcs_timeout
    @wcs_timeout.setter
    def wcs_timeout(self, value):
        self._wcs_timeout = float(value)
        self._config['wcs_timeout'] = str(value)

class TelrunGUI:
    def __init__(self, TelrunOperator):
        self._telrun = TelrunOperator

class TelrunFile:
    pass

class TelrunError(Exception):
    pass