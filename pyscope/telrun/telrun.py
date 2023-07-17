import atexit
import configparser
import os

from pyscope import Observatory, logger

class Telrun:
    def __init__(self, config_file_path=None, **kwargs):

        self._config = configparser.ConfigParser()

        self._observatory = None
        self._autofocus_interval = 3600
        self._initial_autofocus = True
        self._initial_home = True
        self._wait_for_scan_start_time = True
        self._wait_for_sun = True
        self._max_solar_elev = -12
        self._check_safety_monitors = True
        self._max_scan_late_time = 60
        self._preslew_time = 0
        self._hardware_timeout = 60
        self._autofocus_timeout = 180
        self._wcs_timeout = 30

        if config_file_path is not None:
            logger.info('Using config file to initialize telrun: %s' % config_file_path)
            try: self._config.read(config_file_path)
            except: raise TelrunError('Could not read config file: %s' % config_file_path)

            self._observatory = self._config.get('observatory')
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

        self._observatory = kwargs.get('observatory', self._observatory)
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

        if self._observatory is None:
            raise TelrunError('Observatory must be specified')
        elif type(self._observatory) is str:
            self._observatory = Observatory(config_file_path=self._observatory)
        elif type(self._observatory) is not Observatory:
            raise TelrunError('observatory must be a string representing a config file path \
                or an Observatory object')
        
        atexit.register(self.observatory.shutdown())

    def save_config(self, filename):
        directory = os.path.dirname(os.path.abspath(filename))
        self.observatory.save_config(directory + '/'+filename.split('.')[0]+'-observatory.cfg')
        self._config['observatory'] = directory + '/'+filename.split('.')[0]+'-observatory.cfg'
        with open(filename, 'w') as configfile:
            self._config.write(configfile)

    @property
    def observatory(self):
        return self._observatory
    
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
    def check_safety_monitors(self):
        return self._check_safety_monitors
    @check_safety_monitors.setter
    def check_safety_monitors(self, value):
        self._check_safety_monitors = bool(value)
        self._config['check_safety_monitors'] = str(value)

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

class TelrunError(Exception):
    pass