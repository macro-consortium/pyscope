from ast import literal_eval
import configparser
import shutil
import tempfile
import time
import threading

from astropy import coordinates as coord, time as astrotime, units as u
from astropy.io import fits
from astroquery.mpc import MPC
import numpy as np

from . import utils
from .drivers import ascom
from . import __version__, logger

class Observatory:
    '''A class for managing a collection of instruments. The Observatory class provides
    access to special functions that are not available to individual instruments. For example,
    the Observatory class allows a user to save focus offsets for individual filters, which
    requires access to both the filter wheel and the focusing instrument.'''

    def __init__(self, config_file_path=None, **kwargs):
        '''Initializes the observatory. If config_file_path is not None, the observatory will be initialized
        using the config file at config_file_path. Otherwise, the observatory will be initialized using the
        provided objects. If a config file is provided, the objects will be ignored. If no config file is
        provided, the objects must be provided.'''

        self._config = configparser.ConfigParser()
        self._config['site'] = {}
        self._config['camera'] = {}; self._config['cover_calibrator'] = {}; self._config['dome'] = {}
        self._config['filter_wheel'] = {}; self._config['focuser'] = {}; self._config['observing_conditions'] = {}
        self._config['rotator'] = {}; self._config['safety_monitor'] = {}; self._config['switch'] = {}
        self._config['telescope'] = {}; self._config['autofocus'] = {}; self._config['wcs'] = {}

        self._site_name = 'pyScope Site'
        self._instrument_name = 'pyScope Instrument' 
        self._instrument_description = 'pyScope is a pure-Python telescope control package.'
        self._get_site_from_telescope = True
        self._latitude = None; self._longitude = None; self._elevation = None
        self._get_optics_from_telescope = True
        self._diameter = None; self._focal_length = None

        self._camera = None; self._camera_args = None; self._camera_kwargs = None
        self._cooler_setpoint = None; self._cooler_tolerance = None; self._max_dimension = None

        self._cover_calibrator = None; self._cover_calibrator_args = None; self._cover_calibrator_kwargs = None
        self._cover_calibrator_alt = None; self._cover_calibrator_az = None

        self._dome = None; self._dome_args = None; self._dome_kwargs = None

        self._filter_wheel = None; self._filter_wheel_args = None; self._filter_wheel_kwargs = None
        self._filters = None; self._filter_focus_offsets = None

        self._focuser = None; self._focuser_args = None; self._focuser_kwargs = None
        self._focuser_max_error = 10

        self._observing_conditions = None; self._observing_conditions_args = None; self._observing_conditions_kwargs = None

        self._rotator = None; self._rotator_args = None; self._rotator_kwargs = None
        self._rotator_reverse = False; self._rotator_min_angle = None; self._rotator_max_angle = None

        self._safety_monitor = None; self._safety_monitor_args = None; self._safety_monitor_kwargs = None

        self._switch = None; self._switch_args = None; self._switch_kwargs = None

        self._telescope = None; self._telescope_args = None; self._telescope_kwargs = None
        self._min_altitude = 10; self._settle_time = 5

        self._autofocus = None; self._autofocus_args = None; self._autofocus_kwargs = None
        self._wcs = None; self._wcs_args = None; self._wcs_kwargs = None

        self._maxim = None

        if config_file_path is not None:
            logger.info('Using config file to initialize observatory: %s' % config_file)
            try: self._config.read(config_file_path)
            except: raise ObservatoryException("Error parsing config file '%s'" % config_file_path)

            # Camera
            self._camera_driver = self._config['camera']['camera_driver']
            self._camera_ascom = self._config['camera']['camera_ascom']
            self._camera_args = (iter(literal_eval(v) for v in 
                self._config.get('camera', 'camera_args', fallback='').split())
                if self._config.get('camera', 'camera_args', fallback=None) not in (None, '') else None)
            self._camera_kwargs = (dict((k, literal_eval(v)) for k, v in (pair.split(':') 
                for pair in self._config.get('camera', 'camera_kwargs', fallback='').split()))
                if self._config.get('camera', 'camera_kwargs', fallback=None) not in (None, '') else None)
            if self.camera_driver.lower() in ('maxim', 'maximdl'):
                self._maxim = utils.import_driver('Driver', driver_name='Maxim', ascom=False)
                self._camera = self._maxim.camera
            else:
                self._camera = utils.import_driver('Camera', 
                    driver_name=self.camera_driver, 
                    ascom=self.camera_ascom,
                    args=self._camera_args, 
                    kwargs=self._camera_kwargs)

            # Cover calibrator
            self._cover_calibrator_driver = self._config.get('cover_calibrator', 'cover_calibrator_driver', fallback=None)
            self._cover_calibrator_ascom = self._config.get('cover_calibrator', 'cover_calibrator_ascom', fallback=None)
            self._cover_calibrator_args = (iter(literal_eval(v) for v in
                self._config.get('cover_calibrator', 'cover_calibrator_args', fallback='').split())
                if self._config.get('cover_calibrator', 'cover_calibrator_args', fallback=None) not in (None, '') else None)
            self._cover_calibrator_kwargs = (dict((k, literal_eval(v)) for k, v in (pair.split(':')
                for pair in self._config.get('cover_calibrator', 'cover_calibrator_kwargs', fallback='').split()))
                if self._config.get('cover_calibrator', 'cover_calibrator_kwargs', fallback=None) not in (None, '') else None)
            self._cover_calibrator = utils.import_driver('CoverCalibrator', driver_name=self.cover_calibrator_driver, ascom=self.cover_calibrator_ascom, 
                args=self._cover_calibrator_args,
                kwargs=self._cover_calibrator_kwargs)

            # Dome
            self._dome_driver = self._config.get('dome', 'dome_driver', fallback=None)
            self._dome_ascom = self._config.get('dome', 'dome_ascom', fallback=None)
            self._dome_args = (iter(literal_eval(v) for v in
                self._config.get('dome', 'dome_args', fallback='').split())
                if self._config.get('dome', 'dome_args', fallback=None) not in (None, '') else None)
            self._dome_kwargs = (dict((k, literal_eval(v)) for k, v in (pair.split(':')
                for pair in self._config.get('dome', 'dome_kwargs', fallback='').split()))
                if self._config.get('dome', 'dome_kwargs', fallback=None) not in (None, '') else None)
            self._dome = utils.import_driver('Dome', driver_name=self.dome_driver, ascom=self.dome_ascom, 
                args=self._dome_args,
                kwargs=self._dome_kwargs)

            # Filter wheel
            self._filter_wheel_driver = self._config.get('filter_wheel', 'filter_wheel_driver', fallback=None)
            self._filter_wheel_ascom = self._config.get('filter_wheel', 'filter_wheel_ascom', fallback=None)
            self._filter_wheel_args = (iter(literal_eval(v) for v in
                self._config.get('filter_wheel', 'filter_wheel_args', fallback='').split())
                if self._config.get('filter_wheel', 'filter_wheel_args', fallback=None) not in (None, '') else None)
            self._filter_wheel_kwargs = (dict((k, literal_eval(v)) for k, v in (pair.split(':')
                for pair in self._config.get('filter_wheel', 'filter_wheel_kwargs', fallback='').split()))
                if self._config.get('filter_wheel', 'filter_wheel_kwargs', fallback=None) not in (None, '') else None)
            if self.filter_wheel_driver.lower() in ('maxim', 'maximdl'):
                if self._maxim is None:
                    raise ObservatoryException('MaxIm DL must be used as the camera driver when using MaxIm DL as the filter wheel driver.')
                self._filter_wheel = self._maxim.filter_wheel
            else:
                self._filter_wheel = utils.import_driver('FilterWheel', driver_name=self.filter_wheel_driver, ascom=self.filter_wheel_ascom,
                    args=self._filter_wheel_args,
                    kwargs=self._filter_wheel_kwargs)

            # Focuser
            self._focuser_driver = self._config.get('focuser', 'focuser_driver', fallback=None)
            self._focuser_ascom = self._config.get('focuser', 'focuser_ascom', fallback=None)
            self._focuser_args = (iter(literal_eval(v) for v in
                self._config.get('focuser', 'focuser_args', fallback='').split())
                if self._config.get('focuser', 'focuser_args', fallback=None) not in (None, '') else None)
            self._focuser_kwargs = (dict((k, literal_eval(v)) for k, v in (pair.split(':')
                for pair in self._config.get('focuser', 'focuser_kwargs', fallback='').split()))
                if self._config.get('focuser', 'focuser_kwargs', fallback=None) not in (None, '') else None)
            self._focuser = utils.import_driver('Focuser', driver_name=self.focuser_driver, ascom=self.focuser_ascom, 
                kwargs=self._focuser_kwargs)

            # Observing conditions
            self._observing_conditions_driver = self._config.get('observing_conditions', 'observing_conditions_driver', fallback=None)
            self._observing_conditions_ascom = self._config.get('observing_conditions', 'observing_conditions_ascom', fallback=None)
            self._observing_conditions_args = (iter(literal_eval(v) for v in
                self._config.get('observing_conditions', 'observing_conditions_args', fallback='').split())
                if self._config.get('observing_conditions', 'observing_conditions_args', fallback=None) not in (None, '') else None)
            self._observing_conditions_kwargs = (dict((k, literal_eval(v)) for k, v in (pair.split(':')
                for pair in self._config.get('observing_conditions', 'observing_conditions_kwargs', fallback='').split()))
                if self._config.get('observing_conditions', 'observing_conditions_kwargs', fallback=None) not in (None, '') else None)
            self._observing_conditions = utils.import_driver('ObservingConditions', driver_name=self.observing_conditions_driver, 
                ascom=self.observing_conditions_ascom, 
                args=self._observing_conditions_args,
                kwargs=self._observing_conditions_kwargs)

            # Rotator
            self._rotator_driver = self._config.get('rotator', 'rotator_driver', fallback=None)
            self._rotator_ascom = self._config.get('rotator', 'rotator_ascom', fallback=None)
            self._rotator_args = (iter(literal_eval(v) for v in
                self._config.get('rotator', 'rotator_args', fallback='').split())
                if self._config.get('rotator', 'rotator_args', fallback=None) not in (None, '') else None)
            self._rotator_kwargs = (dict((k, literal_eval(v)) for k, v in (pair.split(':')
                for pair in self._config.get('rotator', 'rotator_kwargs', fallback='').split()))
                if self._config.get('rotator', 'rotator_kwargs', fallback=None) not in (None, '') else None)
            self._rotator = utils.import_driver('Rotator', driver_name=self.rotator_driver, ascom=self.rotator_ascom, 
                args=self._rotator_args,
                kwargs=self._rotator_kwargs)

            # Safety monitor
            for val in self._config['safety_monitor'].values():
                try: 
                    driver, ascom, ar, kw = val.split(',')
                    self._safety_monitor_driver.append(driver)
                    self._safety_monitor_ascom.append(ascom)
                    self._safety_monitor_args.append(iter(literal_eval(v) for v in ar.split()) if ar not in (None, '') else None)
                    self._safety_monitor_kwargs.append(dict((k, literal_eval(v)) for k, v in (pair.split(':')
                        for pair in kw.split())) if kw not in (None, '') else None)
                    self._safety_monitor.append(utils.import_driver('SafetyMonitor', driver_name=driver, ascom=ascom, 
                        args=self._safety_monitor_args[-1],
                        kwargs=self._safety_monitor_kwargs[-1]))
                except:
                    logger.warning('Error parsing safety monitor config: %s' % val)

            # Switch
            for val in self._config['switch'].values():
                try: 
                    driver, ascom, kw = val.split(',')
                    self._switch_driver.append(driver)
                    self._switch_ascom.append(ascom)
                    self._switch_args.append(iter(literal_eval(v) for v in ar.split()) if ar not in (None, '') else None)
                    self._switch_kwargs.append(dict((k, literal_eval(v)) for k, v in (pair.split(':')
                        for pair in kw.split())) if kw not in (None, '') else None)
                    self._switch.append(utils.import_driver('Switch', driver_name=driver, ascom=ascom, 
                        args=self._switch_args[-1],
                        kwargs=self._switch_kwargs[-1]))
                except:
                    logger.warning('Error parsing switch config: %s' % val)

            # Telescope
            self._telescope_driver = self._config['telescope']['telescope_driver']
            self._telescope_ascom = self._config['telescope']['telescope_ascom']
            self._telescope_args = (iter(literal_eval(v) for v in
                self._config.get('telescope', 'telescope_args', fallback='').split())
                if self._config.get('telescope', 'telescope_args', fallback=None) not in (None, '') else None)
            self._telescope_kwargs = (dict((k, literal_eval(v)) for k, v in (pair.split(':')
                for pair in self._config.get('telescope', 'telescope_kwargs', fallback='').split()))
                if self._config.get('telescope', 'telescope_kwargs', fallback=None) not in (None, '') else None)
            self._telescope = utils.import_driver('Telescope', driver_name=self.telescope_driver, ascom=self.telescope_ascom, 
                args=self._telescope_args,
                kwargs=self._telescope_kwargs)

            # Autofocus
            self._autofocus_driver = self._config.get('autofocus', 'autofocus_driver', fallback=None)
            self._autofocus_args = (iter(literal_eval(v) for v in
                self._config.get('autofocus', 'autofocus_args', fallback='').split())
                if self._config.get('autofocus', 'autofocus_args', fallback=None) not in (None, '') else None)
            self._autofocus_kwargs = (dict((k, literal_eval(v)) for k, v in (pair.split(':')
                for pair in self._config.get('autofocus', 'autofocus_kwargs', fallback='').split()))
                if self._config.get('autofocus', 'autofocus_kwargs', fallback=None) not in (None, '') else None)
            if self.autofocus_driver in ('maxim', 'maximdl'):
                if self._maxim is None:
                    raise ObservatoryException('MaxIm DL must be used as the camera driver when using MaxIm DL as the autofocus driver.')
                self._autofocus = self._maxim.autofocus
            self._autofocus = utils.import_driver('Autofocus', driver_name=self.autofocus_driver, 
                args=self._autofocus_args,
                kwargs=self._autofocus_kwargs)

            # WCS
            for val in self._config['WCS'].values():
                try:
                    driver, ar, kw = val.split(',')
                    self._wcs_driver.append(val)
                    self._wcs_args.append(iter(literal_eval(v) for v in ar.split()) if ar not in (None, '') else None)
                    self._wcs_kwargs.append(dict((k, literal_eval(v)) for k, v in (pair.split(':')
                        for pair in kw.split())) if kw not in (None, '') else None)
                    if self._wcs_driver in ('maxim', 'maximdl'):
                        if self._maxim is None:
                            raise ObservatoryException('MaxIm DL must be used as the camera driver when using MaxIm DL as the WCS driver.')
                        self._wcs.append(self._maxim.wcs)
                    self._wcs.append(utils.import_driver('WCS', driver_name=val,
                    args=self._wcs_args[-1],
                    kwargs=self._wcs_kwargs[-1]))
                except:
                    logger.warning('Error parsing WCS config: %s' % val)

            # Get other keywords from config file
            logger.debug('Reading other keywords from config file')
            master_dict = {**self._config['site'], **self._config['camera'], **self._config['cover_calibrator'],
                **self._config['dome'], **self._config['filter_wheel'], **self._config['focuser'],
                **self._config['observing_conditions'], **self._config['rotator'], **self._config['safety_monitor'],
                **self._config['switch'], **self._config['telescope'], **self._config['autofocus'], 
                **self._config['wcs']}
            logger.debug('Master dict: %s' % master_dict)
            self._read_out_kwargs(master_dict)
            logger.debug('Finished reading other keywords from config file')

        # Camera
        self._camera = kwargs.get('camera', self._camera)
        utils._check_class_inheritance(type(self._camera), 'Camera')
        self._camera_driver = self._camera.Name
        self._camera_ascom = (ascom.Driver in type(self._camera).__bases__)
        self._camera_args = kwargs.get('camera_args', self._camera_args)
        self._camera_kwargs = kwargs.get('camera_kwargs', self._camera_kwargs)
        self._config['camera']['camera_driver'] = self._camera_driver
        self._config['camera']['camera_ascom'] = str(self._camera_ascom)
        self._config['camera']['camera_args'] = self._args_to_config(self._camera_args)
        self._config['camera']['camera_kwargs'] = self._kwargs_to_config(self._camera_kwargs)

        # Cover calibrator
        self._cover_calibrator = kwargs.get('cover_calibrator', self._cover_calibrator)
        if self._cover_calibrator is None: self._cover_calibrator = _CoverCalibrator(self)
        utils._check_class_inheritance(type(self._cover_calibrator), 'CoverCalibrator')
        self._cover_calibrator_driver = self._cover_calibrator.Name if self._cover_calibrator is not None else ''
        self._cover_calibrator_ascom = (ascom.Driver in type(self._cover_calibrator).__bases__) if self._cover_calibrator is not None else False
        self._cover_calibrator_args = kwargs.get('cover_calibrator_args', self._cover_calibrator_args)
        self._cover_calibrator_kwargs = kwargs.get('cover_calibrator_kwargs', self._cover_calibrator_kwargs)
        self._config['cover_calibrator']['cover_calibrator_driver'] = self._cover_calibrator_driver
        self._config['cover_calibrator']['cover_calibrator_ascom'] = self._cover_calibrator_ascom
        self._config['cover_calibrator']['cover_calibrator_args'] = self._args_to_config(self._cover_calibrator_args)
        self._config['cover_calibrator']['cover_calibrator_kwargs'] = self._kwargs_to_config(self._cover_calibrator_kwargs)

        # Dome
        self._dome = kwargs.get('dome', self._dome)
        if self._dome is not None: utils._check_class_inheritance(type(self._dome), 'Dome')
        self._dome_driver = self._dome.Name if self._dome is not None else ''
        self._dome_ascom = (ascom.Driver in type(self._dome).__bases__) if self._dome is not None else False
        self._dome_args = kwargs.get('dome_args', self._dome_args)
        self._dome_kwargs = kwargs.get('dome_kwargs', self._dome_kwargs)
        self._config['dome']['dome_driver'] = str(self._dome_driver)
        self._config['dome']['dome_ascom'] = str(self._dome_ascom)
        self._config['dome']['dome_args'] = self._args_to_config(self._dome_args)
        self._config['dome']['dome_kwargs'] = self._kwargs_to_config(self._dome_kwargs)

        # Filter wheel
        self._filter_wheel = kwargs.get('filter_wheel', self._filter_wheel)
        if self._filter_wheel is not None: utils._check_class_inheritance(type(self._filter_wheel), 'FilterWheel')
        self._filter_wheel_driver = self._filter_wheel.Name if self._filter_wheel is not None else ''
        self._filter_wheel_ascom = (ascom.Driver in type(self._filter_wheel).__bases__) if self._filter_wheel is not None else False
        self._filter_wheel_args = kwargs.get('filter_wheel_args', self._filter_wheel_args)
        self._filter_wheel_kwargs = kwargs.get('filter_wheel_kwargs', self._filter_wheel_kwargs)
        self._config['filter_wheel']['filter_wheel_driver'] = self._filter_wheel_driver
        self._config['filter_wheel']['filter_wheel_ascom'] = self._filter_wheel_ascom
        self._config['filter_wheel']['filter_wheel_args'] = self._args_to_config(self._filter_wheel_args)
        self._config['filter_wheel']['filter_wheel_kwargs'] = self._kwargs_to_config(self._filter_wheel_kwargs)

        # Focuser
        self._focuser = kwargs.get('focuser', self._focuser)
        if self._focuser is not None: utils._check_class_inheritance(type(self._focuser), 'Focuser')
        self._focuser_driver = self._focuser.Name if self._focuser is not None else ''
        self._focuser_ascom = (ascom.Driver in type(self._focuser).__bases__) if self._focuser is not None else False
        self._focuser_args = kwargs.get('focuser_args', self._focuser_args)
        self._focuser_kwargs = kwargs.get('focuser_kwargs', self._focuser_kwargs)
        self._config['focuser']['focuser_driver'] = self._focuser_driver
        self._config['focuser']['focuser_ascom'] = self._focuser_ascom
        self._config['focuser']['focuser_args'] = self._args_to_config(self._focuser_args)
        self._config['focuser']['focuser_kwargs'] = self._kwargs_to_config(self._focuser_kwargs)

        # Observing conditions
        self._observing_conditions = kwargs.get('observing_conditions', self._observing_conditions)
        if self._observing_conditions is not None: utils._check_class_inheritance(type(self._observing_conditions), 'ObservingConditions')
        self._observing_conditions_driver = self._observing_conditions.Name if self._observing_conditions is not None else ''
        self._observing_conditions_ascom = (ascom.Driver in type(self._observing_conditions).__bases__) if self._observing_conditions is not None else False
        self._observing_conditions_args = kwargs.get('observing_conditions_args', self._observing_conditions_args)
        self._observing_conditions_kwargs = kwargs.get('observing_conditions_kwargs', self._observing_conditions_kwargs)
        self._config['observing_conditions']['observing_conditions_driver'] = self._observing_conditions_driver
        self._config['observing_conditions']['observing_conditions_ascom'] = self._observing_conditions_ascom
        self._config['observing_conditions']['observing_conditions_args'] = self._args_to_config(self._observing_conditions_args)
        self._config['observing_conditions']['observing_conditions_kwargs'] = self._kwargs_to_config(self._observing_conditions_kwargs)

        # Rotator
        self._rotator = kwargs.get('rotator', self._rotator)
        if self._rotator is not None: utils._check_class_inheritance(type(self._rotator), 'Rotator')
        self._rotator_driver = self._rotator.Name if self._rotator is not None else ''
        self._rotator_ascom = (ascom.Driver in type(self._rotator).__bases__) if self._rotator is not None else False
        self._rotator_args = kwargs.get('rotator_args', self._rotator_args)
        self._rotator_kwargs = kwargs.get('rotator_kwargs', self._rotator_kwargs)
        self._config['rotator']['rotator_driver'] = self._rotator_driver
        self._config['rotator']['rotator_ascom'] = self._rotator_ascom
        self._config['rotator']['rotator_args'] = self._args_to_config(self._rotator_args)
        self._config['rotator']['rotator_kwargs'] = self._kwargs_to_config(self._rotator_kwargs)

        # Safety monitor
        kwarg = kwargs.get('safety_monitor', self._safety_monitor)
        if type(kwarg) not in (iter, list, tuple): 
            self._safety_monitor = kwarg
            if self._safety_monitor is not None: utils._check_class_inheritance(type(self._safety_monitor), 'SafetyMonitor')
            self._safety_monitor_driver = self._safety_monitor.Name if self._safety_monitor is not None else ''
            self._safety_monitor_ascom = (ascom.Driver in type(self._safety_monitor).__bases__) if self._safety_monitor is not None else False
            self._safety_monitor_args = kwargs.get('safety_monitor_args', self._safety_monitor_args)
            self._safety_monitor_kwargs = kwargs.get('safety_monitor_kwargs', self._safety_monitor_kwargs)
            self._config['safety_monitor']['driver_0'] = (self._safety_monitor_driver 
                + ',' + str(self._safety_monitor_ascom)
                + ',' + self._args_to_config(self._safety_monitor_args)
                + ',' + self._kwargs_to_config(self._safety_monitor_kwargs)
                ) if self._safety_monitor_driver != '' else ''
        else: 
            self._safety_monitor = kwarg
            self._safety_monitor_driver = [None] * len(self._safety_monitor)
            self._safety_monitor_ascom = [None] * len(self._safety_monitor)
            self._safety_monitor_args = [None] * len(self._safety_monitor)
            self._safety_monitor_kwargs = [None] * len(self._safety_monitor)
            for i, safety_monitor in enumerate(self._safety_monitor):
                if safety_monitor is not None: utils._check_class_inheritance(type(safety_monitor), 'SafetyMonitor')
                self._safety_monitor_driver[i] = safety_monitor.Name if safety_monitor is not None else ''
                self._safety_monitor_ascom[i] = (ascom.Driver in type(safety_monitor).__bases__) if safety_monitor is not None else False
                self._safety_monitor_args[i] = kwargs.get('safety_monitor_args', None)[i] if kwargs.get('safety_monitor_args', None) is not None else None
                self._safety_monitor_kwargs[i] = kwargs.get('safety_monitor_kwargs', None)[i] if kwargs.get('safety_monitor_kwargs', None) is not None else None
                self._config['safety_monitor']['driver_%i' % i] = (self._safety_monitor_driver[i] 
                    + ',' + str(self._safety_monitor_ascom[i]) 
                    + ',' + self._args_to_config(self._safety_monitor_args[i])
                    + ',' + self._kwargs_to_config(self._safety_monitor_kwargs[i])
                    ) if self._safety_monitor_driver[i] != '' else ''

        # Switch
        kwarg = kwargs.get('switch', self._switch)
        if type(kwarg) not in (iter, list, tuple): 
            self._switch = kwarg
            if self._switch is not None: utils._check_class_inheritance(type(self._switch), 'Switch')
            self._switch_driver = self._switch.Name if self._switch is not None else ''
            self._switch_ascom = (ascom.Driver in type(self._switch).__bases__) if self._switch is not None else False
            self._switch_args = kwargs.get('switch_args', self._switch_args)
            self._switch_kwargs = kwargs.get('switch_kwargs', self._switch_kwargs)
            self._config['switch']['driver_0'] = (self._switch_driver
                + ',' + str(self._switch_ascom)
                + ',' + self._args_to_config(self._switch_args)
                + ',' + self._kwargs_to_config(self._switch_kwargs)
                ) if self._switch_driver != '' else ''
        else: 
            self._switch = kwarg
            self._switch_driver = [None] * len(self._switch)
            self._switch_ascom = [None] * len(self._switch)
            self._switch_args = [None] * len(self._switch)
            self._switch_kwargs = [None] * len(self._switch)
            for i, switch in enumerate(self._switch):
                if switch is not None: utils._check_class_inheritance(switch, 'Switch')
                self._switch_driver[i] = switch.Name if switch is not None else ''
                self._switch_ascom[i] = (ascom.Driver in type(switch).__bases__) if switch is not None else False
                self._switch_args[i] = kwargs.get('switch_args', None)[i] if kwargs.get('switch_args', None) is not None else None
                self._switch_kwargs[i] = kwargs.get('switch_kwargs', None)[i] if kwargs.get('switch_kwargs', None) is not None else None
                self._config['switch']['driver_%i' % i] = (
                    self._switch_driver[i]
                    + ',' + str(self._switch_ascom[i])
                    + ',' + self._args_to_config(self._switch_args[i])
                    + ',' + self._kwargs_to_config(self._switch_kwargs[i])
                    ) if self._switch_driver[i] != '' else ''

        # Telescope
        self._telescope = kwargs.get('telescope', self._telescope)
        utils._check_class_inheritance(type(self._telescope), 'Telescope')
        self._telescope_driver = self._telescope.Name
        self._telescope_ascom = (ascom.Driver in type(self._telescope).__bases__)
        self._telescope_args = kwargs.get('telescope_args', self._telescope_args)
        self._telescope_kwargs = kwargs.get('telescope_kwargs', self._telescope_kwargs)
        self._config['telescope']['telescope_driver'] = self._telescope_driver
        self._config['telescope']['telescope_ascom'] = str(self._telescope_ascom)
        self._config['telescope']['telescope_args'] = self._args_to_config(self._telescope_args)
        self._config['telescope']['telescope_kwargs'] = self._kwargs_to_config(self._telescope_kwargs)

        # Autofocus
        self._autofocus = kwargs.get('autofocus', self._autofocus)
        if self._autofocus is not None: utils._check_class_inheritance(type(self._autofocus), 'Autofocus')
        self._autofocus_driver = self._autofocus.Name if self._autofocus is not None else ''
        self._autofocus_args = kwargs.get('autofocus_args', self._autofocus_args)
        self._autofocus_kwargs = kwargs.get('autofocus_kwargs', self._autofocus_kwargs)
        self._config['autofocus']['autofocus_driver'] = self._autofocus_driver
        self._config['autofocus']['autofocus_args'] = self._args_to_config(self._autofocus_args)
        self._config['autofocus']['autofocus_kwargs'] = self._kwargs_to_config(self._autofocus_kwargs)

        # WCS
        kwarg = kwargs.get('wcs', self._wcs)
        if kwarg is None:
            self._wcs = utils.import_driver('WCS', 'wcs_astrometrynet')
            self._wcs_driver = 'wcs_astrometrynet'
            self._config['wcs']['driver_0'] = self._wcs_driver
        elif type(kwarg) not in (iter, list, tuple):
            self._wcs = kwarg
            utils._check_class_inheritance(type(self._wcs), 'WCS')
            self._wcs_driver = self._wcs.__name__ if self._wcs is not None else ''
            self._wcs_args = kwargs.get('wcs_args', self._wcs_args)
            self._wcs_kwargs = kwargs.get('wcs_kwargs', self._wcs_kwargs)
            self._config['wcs']['driver_0'] = (self._wcs_driver
                + ',' + self._args_to_config(self._wcs_args)
                + ',' + self._kwargs_to_config(self._wcs_kwargs)
                ) if self._wcs_driver != '' else ''
        else:
            self._wcs = kwarg
            self._wcs_driver = [None] * len(self._wcs)
            self._wcs_args = [None] * len(self._wcs)
            self._wcs_kwargs = [None] * len(self._wcs)
            for i, wcs in enumerate(self._wcs):
                if wcs is not None: utils._check_class_inheritance(wcs, 'WCS')
                self._wcs_driver[i] = wcs.__name__ if wcs is not None else ''
                self._wcs_args[i] = kwargs.get('wcs_args', None)[i] if kwargs.get('wcs_args', None) is not None else None
                self._wcs_kwargs[i] = kwargs.get('wcs_kwargs', None)[i] if kwargs.get('wcs_kwargs', None) is not None else None
                self._config['wcs']['driver_%i' % i] = (
                    self._wcs_driver[i]
                    + ',' + self._args_to_config(self._wcs_args[i])
                    + ',' + self._kwargs_to_config(self._wcs_kwargs[i])
                    ) if self._wcs_driver[i] != '' else ''

        logger.debug('Reading out keywords passed as kwargs')
        logger.debug('kwargs: %s' % kwargs)
        self._read_out_kwargs(kwargs)
        logger.debug('kwargs read out')

        # Non-keyword properties
        self._last_camera_shutter_status = None
        self.camera.OriginalStartExposure = self.camera.StartExposure
        def NewStartExposure(self, Duration, Light):
            self._last_camera_shutter_status = Light
            self.camera.OriginalStartExposure(Duration, Light)
        self.camera.StartExposure = NewStartExposure

        self._current_focus_offset = 0
        
        # Threads
        self._observing_conditions_thread = None
        self._observing_conditions_event = None

        self._safety_monitor_thread = None
        self._safety_monitor_event = None

        self.derotation_thread = None
        self.derotation_event = None

        logger.debug('Config:')
        logger.debug(self._config)
    
    def connect_all(self):        

        self.camera.Connected = True
        if self.camera.Connected: logger.info('Camera connected')
        else: logger.warning('Camera failed to connect')

        if self.cover_calibrator is not None:
            self.cover_calibrator.Connected = True
            if self.cover_calibrator.Connected: logger.info('Cover calibrator connected')
            else: logger.warning('Cover calibrator failed to connect')
        
        if self.dome is not None:
            self.dome.Connected = True
            if self.dome.Connected: logger.info('Dome connected')
            else: logger.warning('Dome failed to connect')
        
        if self.filter_wheel is not None:
            self.filter_wheel.Connected = True
            if self.filter_wheel.Connected: logger.info('Filter wheel connected')
            else: logger.warning('Filter wheel failed to connect')
        
        if self.focuser is not None:
            self.focuser.Connected = True
            if self.focuser.Connected: logger.info('Focuser connected')
            else: logger.warning('Focuser failed to connect')
        
        if self.observing_conditions is not None:
            self.observing_conditions.Connected = True
            if self.observing_conditions.Connected: logger.info('Observing conditions connected')
            else: logger.warning('Observing conditions failed to connect')
        
        if self.rotator is not None:
            self.rotator.Connected = True
            if self.rotator.Connected: logger.info('Rotator connected')
            else: logger.warning('Rotator failed to connect')
        
        if self.safety_monitor is not None:
            for safety_monitor in self.safety_monitor:
                safety_monitor.Connected = True
                if safety_monitor.Connected: logger.info('Safety monitor %s connected' % safety_monitor.Name)
                else: logger.warning('Safety monitor %s failed to connect' % safety_monitor.Name)
            
        if self.switch is not None:
            for switch in self.switch:
                switch.Connected = True
                if switch.Connected: logger.info('Switch %s connected' % switch.Name)
                else: logger.warning('Switch %s failed to connect' % switch.Name)
        
        self.telescope.Connected = True
        if self.telescope.Connected: logger.info('Telescope connected')
        else: logger.warning('Telescope failed to connect')

        return True
    
    def disconnect_all(self):
        '''Disconnects from the observatory'''

        self.camera.Connected = False
        if not self.camera.Connected: logger.info('Camera disconnected')
        else: logger.warning('Camera failed to disconnect')

        if self.cover_calibrator is not None:
            self.cover_calibrator.Connected = False
            if not self.cover_calibrator.Connected: logger.info('Cover calibrator disconnected')
            else: logger.warning('Cover calibrator failed to disconnect')
        
        if self.dome is not None:
            self.dome.Connected = False
            if not self.dome.Connected: logger.info('Dome disconnected')
            else: logger.warning('Dome failed to disconnect')
        
        if self.filter_wheel is not None:
            self.filter_wheel.Connected = False
            if not self.filter_wheel.Connected: logger.info('Filter wheel disconnected')
            else: logger.warning('Filter wheel failed to disconnect')
        
        if self.focuser is not None:
            self.focuser.Connected = False
            if not self.focuser.Connected: logger.info('Focuser disconnected')
            else: logger.warning('Focuser failed to disconnect')

        if self.observing_conditions is not None:
            self.observing_conditions.Connected = False
            if not self.observing_conditions.Connected: logger.info('Observing conditions disconnected')
            else: logger.warning('Observing conditions failed to disconnect')
        
        if self.rotator is not None:
            self.rotator.Connected = False
            if not self.rotator.Connected: logger.info('Rotator disconnected')
            else: logger.warning('Rotator failed to disconnect')
        
        if self.safety_monitor is not None:
            for safety_monitor in self.safety_monitor:
                safety_monitor.Connected = False
                if not safety_monitor.Connected: logger.info('Safety monitor %s disconnected' % safety_monitor.Name)
                else: logger.warning('Safety monitor %s failed to disconnect' % safety_monitor.Name)
        
        if self.switch is not None:
            for switch in self.switch:
                switch.Connected = False
                if not switch.Connected: logger.info('Switch %s disconnected' % switch.Name)
                else: logger.warning('Switch %s failed to disconnect' % switch.Name)
            
        self.telescope.Connected = False
        if not self.telescope.Connected: logger.info('Telescope disconnected')
        else: logger.warning('Telescope failed to disconnect')

        return True
    
    def shutdown(self):
        '''Shuts down the observatory'''

        logger.info('Shutting down observatory')

        if self.camera.CanAbortExposure:
            logger.info('Aborting any in-progress camera exposures...')
            try: self.camera.AbortExposure(); logger.info('Camera exposure aborted')
            except: logger.exception('Error aborting exposure during shutdown')

        logger.info('Attempting to take a dark exposure to close camera shutter...')
        try:
            self.camera.StartExposure(0, False)
            while self.camera.ImageReady is False:
                time.sleep(0.1)
            logger.info('Dark exposure complete')
        except: logger.exception('Error closing camera shutter during shutdown')
    
        if self.cover_calibrator is not None:
            if self.cover_calibrator.CalibratorState != 'NotPresent':
                logger.info('Attempting to turn off cover calibrator...')
                try: self.cover_calibrator.CalibratorOff(); logger.info('Cover calibrator turned off')
                except: logger.exception('Error turning off cover calibrator during shutdown')
            if self.cover_calibrator.CoverState != 'NotPresent':
                logger.info('Attempting to halt any cover calibrator shutter motion...')
                try: self.cover_calibrator.HaltCover(); logger.info('Cover calibrator shutter motion halted')
                except: logger.exception('Error closing cover calibrator shutter during shutdown')
                logger.info('Attempting to close cover calibrator shutter...')
                try: self.cover_calibrator.CloseCover(); logger.info('Cover calibrator shutter closed')
                except: logger.exception('Error closing cover calibrator shutter during shutdown')

        if self.dome is not None:
            logger.info('Aborting any dome motion...')
            try: self.dome.AbortSlew(); logger.info('Dome motion aborted')
            except: logger.exception('Error aborting dome motion during shutdown')

            if self.dome.CanFindPark:
                logger.info('Attempting to park dome...')
                try: self.dome.Park(); logger.info('Dome parked')
                except: logger.exception('Error parking dome during shutdown')

            if self.dome.CanSetShutter:
                logger.info('Attempting to close dome shutter...')
                try: self.dome.CloseShutter(); logger.info('Dome shutter closed')
                except: logger.exception('Error closing dome shutter during shutdown')
        
        if self.focuser is not None:
            logger.info('Aborting any in-progress focuser motion...')
            try: self.focuser.Halt(); logger.info('Focuser motion aborted')
            except: logger.exception('Error aborting focuser motion during shutdown')
        
        if self.rotator is not None:
            logger.info('Aborting any in-progress rotator motion...')
            try: self.rotator.Halt(); logger.info('Rotator motion aborted')
            except: logger.exception('Error stopping rotator during shutdown')
        
        logger.info('Aborting any in-progress telescope slews...')
        try: self.telescope.AbortSlew(); logger.info('Telescope slew aborted')
        except: logger.exception('Error aborting slew during shutdown')

        logger.info('Attempting to turn off telescope tracking...')
        try: self.telescope.Tracking = False; logger.info('Telescope tracking turned off')
        except: logger.exception('Error turning off telescope tracking during shutdown')

        if self.telescope.CanPark:
            logger.info('Attempting to park telescope...')
            try: self.telescope.Park(); logger.info('Telescope parked')
            except: logger.exception('Error parking telescope during shutdown')
        elif self.telescope.CanFindHome:
            logger.info('Attempting to find home position...')
            try: self.telescope.FindHome(); logger.info('Telescope home position found')
            except: logger.exception('Error finding home position during shutdown')

        return True
        
    def lst(self, t=None):
        '''Returns the local sidereal time'''

        if t is None: t = self.observatory_time
        else: t = Time(t)
        return t.sidereal_time('apparent', self.observatory_location).to('hourangle').value
        
    def sun_altaz(self, t=None):
        '''Returns the altitude of the sun'''

        if t is None: t = self.observatory_time
        else: t = Time(t)

        sun = coord.get_sun(t).transform_to(coord.AltAz(obstime=t, location=self.observatory_location))

        return (sun.alt.deg, sun.az.deg)
    
    def moon_altaz(self, t=None):
        '''Returns the current altitude of the moon'''

        if t is None: t = self.observatory_time
        else: t = Time(t)

        moon = coord.get_moon(t).transform_to(coord.AltAz(obstime=t, location=self.observatory_location))

        return (moon.alt.deg, moon.az.deg)
    
    def moon_illumination(self, t=None):
        '''Returns the current illumination of the moon'''

        if t is None: t = self.observatory_time
        else: t = Time(t)

        sun = coord.get_sun(t); moon = coord.get_moon(t)
        elongation = sun.separation(moon)
        phase_angle = np.arctan2(sun.distance*np.sin(elongation), moon.distance - sun.distance*np.cos(elongation))
        return (1.0 + np.cos(phase_angle))/2.0

    def get_object_altaz(self, obj=None, ra=None, dec=None, unit=('hr', 'deg'), frame='icrs', t=None):
        '''Returns the altitude and azimuth of the requested object at the requested time'''
        obj = self._parse_obj_ra_dec(obj, ra, dec, unit, frame)
        if t is None: t = self.observatory_time
        t = Time(t)

        return obj.transform_to(coord.AltAz(obstime=t, location=self.observatory_location))
    
    def get_object_slew(self, obj=None, ra=None, dec=None, unit=('hr', 'deg'), frame='icrs', t=None):
        '''Determines the slew coordinates of the requested object at the requested time'''
        obj = self._parse_obj_ra_dec(obj, ra, dec, unit, frame)
        if t is None: t = self.observatory_time
        t = Time(t)

        eq_system = self.telescope.EquatorialSystem
        if eq_system == 0:
            logger.warning('Telescope equatorial system is not set, assuming Topocentric')
            eq_system = 1
        
        if eq_system == 1: obj_slew = obj.transform_to(coord.TETE(obstime=t, location=self.observatory_location))
        elif eq_system == 2: obj_slew = obj.transform_to('icrs')
        elif eq_system == 3:
            logger.info('Astropy does not support J2050 ICRS yet, using FK5')
            obj_slew = obj.transform_to(coord.FK5(equinox='J2050'))
        elif eq_system == 4: obj_slew = obj.transform_to(coord.FK4(equinox='B1950'))

        return obj_slew
    
    def get_current_object(self):
        '''Returns the current pointing of the telescope in ICRS'''
        eq_system = self.telescope.EquatorialSystem
        if eq_system in (0, 1): obj = self._parse_obj_ra_dec(ra=self.telescope.RightAscension, dec=self.telescope.Declination, 
                frame=coord.TETE(obstime=t, location=self.observatory_location))
        elif eq_system == 2: obj = self._parse_obj_ra_dec(ra=self.telescope.RightAscension, dec=self.telescope.Declination)
        elif eq_system == 3: obj = self._parse_obj_ra_dec(ra=self.telescope.RightAscension, dec=self.telescope.Declination,
                frame=coord.FK5(equinox='J2050'))
        elif eq_system == 4: obj = self._parse_obj_ra_dec(ra=self.telescope.RightAscension, dec=self.telescope.Declination,
                frame=coord.FK4(equinox='B1950'))
        return obj
    
    def save_last_image(self, filename, frametyp=None, do_wcs=False, do_fwhm=False, overwrite=False, 
                        custom_header=None, **kwargs):
        '''Saves the current image'''

        if not self.camera.ImageReady:
            logger.exception('Image is not ready, cannot be saved')
            return False
        
        if (self.camera.ImageArray is None or self.camera.ImageArray.size == 0 
            or self.camera.ImageArray.shape[0] == 0 or self.camera.ImageArray.shape[1] == 0):
            logger.exception('Image array is empty, cannot be saved')
            return False
        
        hdr = fits.Header()

        hdr['SIMPLE'] = True
        hdr['BITPIX'] = (16, '8 unsigned int, 16 & 32 int, -32 & -64 real')
        hdr['NAXIS'] = (2, 'number of axes')
        hdr['NAXIS1'] = (self.camera.ImageArray.shape[0], 'fastest changing axis')
        hdr['NAXIS2'] = (self.camera.ImageArray.shape[1], 'next to fastest changing axis')
        hdr['BSCALE'] = (1, 'physical=BZERO + BSCALE*array_value')
        hdr['BZERO'] = (32768, 'physical=BZERO + BSCALE*array_value')
        hdr['SWCREATE'] = ('pyScope', 'Software used to create file')
        hdr['SWVERSIO'] = (__version__, 'Version of software used to create file')
        hdr['ROWORDER'] = ('TOP-DOWN', 'Row order of image')

        if frametyp is not None: hdr['FRAMETYP'] = (frametyp, 'Frame type')
        elif self.last_camera_shutter_status: hdr['FRAMETYP'] = ('Light', 'Frame type') 
        elif not self.last_camera_shutter_status: hdr['FRAMETYP'] = ('Dark', 'Frame type')

        hdr.update(self.observatory_info)
        hdr.update(self.camera_info)
        hdr.update(self.telescope_info)
        hdr.update(self.cover_calibrator_info)
        hdr.update(self.dome_info)
        hdr.update(self.filter_wheel_info)
        hdr.update(self.focuser_info)
        hdr.update(self.observing_conditions_info)
        hdr.update(self.rotator_info)
        hdr.update(self.safety_monitor_info)
        hdr.update(self.switch_info)
        hdr.update(self.threads_info)
        hdr.update(self.autofocus_info)
        hdr.update(self.wcs_info)

        if custom_header is not None: hdr.update(custom_header)

        if do_fwhm:
            logger.info('Attempting to measure FWHM')
            cat = utils.get_image_source_catalog(filename)

            hdr['FWHMH'] = (np.median(np.sqrt(cat.covar_sigx2)), 'Median FWHM in horizontal direction')
            hdr['FWHMHS'] = (np.std(np.sqrt(cat.covar_sigx2)), 'Std. dev. of FWHM in horizontal direction')
            hdr['FWHMV'] = (np.median(np.sqrt(cat.covar_sigy2)), 'Median FWHM in vertical direction')
            hdr['FWHMVS'] = (np.std(np.sqrt(cat.covar_sigy2)), 'Std. dev. of FWHM in vertical direction')
            logger.info('FWHMH: %.2f +/- %.2f' % (hdr['FWHMH'], hdr['FWHMHS']))
            logger.info('FWHMV: %.2f +/- %.2f' % (hdr['FWHMV'], hdr['FWHMVS']))

        hdu = fits.PrimaryHDU(self.camera.ImageArray, header=hdr)
        hdu.writeto(filename, overwrite=overwrite)

        if do_wcs: 
            logger.info('Attempting to solve image for WCS')
            if type(self.wcs) is WCS:
                logger.info('Using solver %s' % self.wcs_driver)
                self.wcs.Solve(filename, ra_key='OBJCTRA', dec_key='OBJCTDEC', 
                    ra_dec_units=('hour', 'deg'), solve_timeout=60, 
                    scale_units='arcsecperpix', scale_type='ev',
                    scale_est=self.pixel_scale[0], scale_err=self.pixel_scale[0]*0.1,
                    parity=1, crpix_center=True)
            else: 
                for wcs, i in enumerate(self.wcs):
                    logger.info('Using solver %s' % self.wcs_driver[i])
                    solution = wcs.Solve(filename, ra_key='OBJCTRA', dec_key='OBJCTDEC',
                        ra_dec_units=('hour', 'deg'), solve_timeout=60,
                        scale_units='arcsecperpix', scale_type='ev',
                        scale_est=self.pixel_scale[0], scale_err=self.pixel_scale[0]*0.1,
                        parity=1, crpix_center=True)
                    if solution: break
                if not solution: logger.warning('WCS solution not found.')

        return True
    
    def set_filter_offset_focuser(self, filter_index=None, filter_name=None):
        if filter_index is None:
            try: 
                filter_index = self.filters.index(filter_name)
                logger.info('Filter %s found at index %i' % (filter_name, filter_index))
            except:
                raise ObservatoryException('Filter %s not found in filter list' % filter_name)

        if self.filter_wheel is not None:
            if self.filter_wheel.Connected:
                logger.info('Setting filter wheel to filter %i' % filter_index)
                self.filter_wheel.Position = filter_index
                logger.info('Filter wheel set')
            else:   
                raise ObservatoryException('Filter wheel is not connected.')
        else:
            raise ObservatoryException('There is no filter wheel.')
        
        if self.focuser is not None:
            if self.focuser.Connected:
                self._current_focus_offset = (self.filter_focus_offsets[filter_index]
                                                - self.current_focus_offset)

                if self.current_focus_offset < self.focuser.MaxIncrement:
                    if self.focuser.Absolute:
                        if (self.focuser.Position + self.current_focus_offset > 0 
                                and self.focuser.Position + self.current_focus_offset < self.focuser.MaxStep):
                            logger.info('Focuser moving to position %i' % (self.focuser.Position + self.current_focus_offset))
                            self.focuser.Move(self.focuser.Position + self.current_focus_offset)
                            logger.info('Focuser moved')
                        else:
                            raise ObservatoryException('Focuser cannot move to the requested position.')
                    else:
                        logger.info('Focuser moving to relative position %i' % self.current_focus_offset)
                        self.focuser.Move(self.current_focus_offset)
                        logger.info('Focuser moved')
                else: 
                    raise ObservatoryException('Focuser cannot move to the requested position.')
            else:
                raise ObservatoryException('Focuser is not connected.')
        else: 
            logger.warning('There is no focuser, skipping setting an offset.')

    
    def slew_to_coordinates(self, obj=None, ra=None, dec=None, unit=('hr', 'deg'), frame='icrs', 
                            control_dome=False, control_rotator=False, home_first=False, 
                            wait_for_slew=True, track=True):
        '''Slews the telescope to a given ra and dec'''

        obj = self._parse_obj_ra_dec(obj, ra, dec, unit, frame)

        logger.info('Slewing to RA %i:%i:%.2f and Dec %i:%i:%.2f' % obj.ra.hms[0], obj.ra.hms[1], obj.ra.hms[2],
            obj.dec.dms[0], obj.dec.dms[1], obj.dec.dms[2])
        slew_obj = self.get_object_slew(obj)
        altaz_obj = self.get_object_altaz(obj)

        if not self.telescope.Connected: raise ObservatoryException('The telescope is not connected.')

        if altaz_obj.alt.deg <= self.min_altitude:
            logger.exception('Target is below the minimum altitude of %.2f degrees' % self.min_altitude)
            return False
        
        if control_rotator and self.rotator is not None:
            self.stop_derotation_thread()
        
        if self.telescope.CanPark:
            if self.telescope.AtPark:
                logger.info('Telescope is parked, unparking...')
                self.telescope.Unpark(); logger.info('Unparked.')
                if self.telescope.CanFindHome and home_first:
                    logger.info('Finding home position...')
                    self.telescope.FindHome(); logger.info('Found home position.')
        
        logger.info('Attempting to slew to coordinates...')
        if self.telescope.CanSlew: 
            if self.telescope.CanSlewAsync: self.telescope.SlewToCoordinatesAsync(slew_obj.ra.hour, slew_obj.dec.deg)
            else: self.telescope.SlewToCoordinates(slew_obj.ra.hour, slew_obj.dec.deg)
        elif self.telescope.CanSlewAltAz:
            if self.telescope.CanSlewAltAzAsync: self.telescope.SlewToAltAzAsync(altaz_obj.alt.deg, altaz_obj.az.deg)
            else: self.telescope.SlewToAltAz(altaz_obj.alt.deg, altaz_obj.az.deg)
        else: raise ObservatoryException('The telescope cannot slew to coordinates.')

        if control_dome and self.dome is not None:
            if self.dome.ShutterState != 0 and self.CanSetShutter:
                logger.info('Opening the dome shutter...')
                self.dome.OpenShutter(); logger.info('Opened.')
                if self.dome.CanFindHome:
                    logger.info('Finding the dome home...')
                    self.dome.FindHome(); logger.info('Found.')
            if self.dome.CanPark:
                if self.dome.AtPark and self.dome.CanFindHome:
                    logger.info('Finding the dome home...')
                    self.dome.FindHome(); logger.info('Found.')
            if not self.dome.Slaved:
                if self.dome.CanSetAltitude: 
                    logger.info('Setting the dome altitude...')
                    self.dome.SlewToAltitude(altaz_obj.alt.deg); logger.info('Set.')
                if self.dome.CanSetAzimuth: 
                    logger.info('Setting the dome azimuth...'); logger.info('Set.')
                    self.dome.SlewToAzimuth(altaz_obj.az.deg)

        if control_rotator and self.rotator is not None:
            rotation_angle = (self.lst() - slew_obj.ra.hour) * 15

            if (self.rotator.MechanicalPosition + rotation_angle >= self.rotator_max_angle or
                self.rotator.MechanicalPosition - rotation_angle <= self.rotator_min_angle):
                logger.warning('Rotator will pass through the limit. Cannot slew to target.')
                control_rotator = False

            logger.info('Rotating the rotator to hour angle %.2f' % hour_angle)
            self.rotator.MoveAbsolute(rotation_angle); logger.info('Rotated.')

        condition = wait_for_slew
        while condition:
            condition = self.telescope.Slewing
            if self.control_dome and self.dome is not None: condition = condition or self.dome.Slewing
            if self.control_rotator and self.rotator is not None: condition = condition or self.rotator.IsMoving
            time.sleep(0.1)
        else:
            logger.info('Settling for %.2f seconds...' % self.settle_time)
            time.sleep(self.settle_time)

        if track and self.telescope.CanSetTracking: 
            logger.info('Turning on sidereal tracking...')
            self.telescope.TrackingRate = 0
            self.telescope.Tracking = True
            logger.info('Sidereal tracking is on.')
        else: logger.warning('Tracking cannot be turned on.')

        return True
    
    def start_observing_conditions_thread(self, update_interval=60):
        '''Starts the observing conditions updating thread'''

        if self.observing_conditions is None: raise ObservatoryException('There is no observing conditions object.')

        logger.info('Starting observing conditions thread...')
        self._observing_conditions_event = threading.Event()
        self._observing_conditions_thread = threading.Thread(target=self._update_observing_conditions, args=(update_interval,), 
            daemon=True, name='Observing Conditions Thread')
        self._observing_conditions_thread.start()
        logger.info('Observing conditions thread started.')

        return True
    
    def stop_observing_conditions_thread(self):
        '''Stops the observing conditions updating thread'''

        if self._observing_conditions_event is None:
            logger.warning('Observing conditions thread is not running.')
            return False

        logger.info('Stopping observing conditions thread...')
        self._observing_conditions_event.set()
        self._observing_conditions_thread.join()
        self._observing_conditions_event = None
        self._observing_conditions_thread = None
        logger.info('Observing conditions thread stopped.')

        return True

    def _update_observing_conditions(self, wait_time=0):
        '''Updates the observing conditions'''
        while not self._observing_conditions_event.is_set():
            logger.debug('Updating observing conditions...')
            self.observing_conditions.Refresh()
            time.sleep(wait_time)
    
    def start_safety_monitor_thread(self, on_fail=None, update_interval=60):
        '''Starts the safety monitor updating thread'''

        if self.safety_monitor is None: raise ObservatoryException('Safety monitor is not connected.')

        if on_fail is None:
            logger.info('No safety monitor failure function provided. Using default shutdown function')
            on_fail = self.shutdown

        logger.info('Starting safety monitor thread...')
        self._safety_monitor_event = threading.Event()
        self._safety_monitor_thread = threading.Thread(target=self._update_safety_monitor, args=(on_fail,update_interval,), 
            daemon=True, name='Safety Monitor Thread')
        self._safety_monitor_thread.start()
        logger.info('Safety monitor thread started.')

        return True
    
    def stop_safety_monitor_thread(self):
        '''Stops the safety monitor updating thread'''

        if self._safety_monitor_event is None:
            logger.warning('Safety monitor thread is not running.')
            return False

        logger.info('Stopping safety monitor thread...')
        self._safety_monitor_event.set()
        self._safety_monitor_thread.join()
        self._safety_monitor_event = None
        self._safety_monitor_thread = None
        logger.info('Safety monitor thread stopped.')

        return True
    
    def _update_safety_monitor(self, on_fail, wait_time=0):
        '''Updates the safety monitor'''
        while not self._safety_monitor_event.is_set():
            logger.debug('Updating safety monitor...')
            safety_array = self.safety_status()
            if not all(safety_array):
                logger.warning('Safety monitor is not safe, calling on_fail function "%s" and ending thread...' % on_fail.__name__)
                on_fail()
                self.stop_safety_monitor_thread()
                return
            time.sleep(wait_time)

    def start_derotation_thread(self, update_interval=0.05):
        '''Begin a derotation thread for the current ra and dec'''

        if self.rotator is None: raise ObservatoryException('There is no rotator object.')

        obj = self.get_current_object().transform_to(coord.AltAz(obstime=Time.now(), location=self.location))

        logger.info('Starting derotation thread...')
        self._derotation_event = threading.Event()
        self._derotation_thread = threading.Thread(target=self._update_rotator, args=(obj,), 
            daemon=True, name='Derotation Thread')
        self._derotation_thread.start()
        logger.info('Derotation thread started.')

        return True

    def stop_derotation_thread(self):
        '''Stops the derotation thread'''

        if self._derotation_event is None:
            logger.warning('Derotation thread is not running.')
            return False

        logger.info('Stopping derotation thread...')
        self._derotation_event.set()
        self._derotation_thread.join()
        self._derotation_event = None
        self._derotation_thread = None
        logger.info('Derotation thread stopped.')

        return True
    
    def _update_rotator(self, obj, wait_time=0):
        '''Updates the rotator'''
        # mean sidereal rate (at J2000) in radians per second
        SR = 7.292115855306589e-5

        while not self._derotation_event.is_set():
            self.rotator.Move(command)

            t0 = self.observatory_time
            obj = obj.transform_to(coord.AltAz(obstime=t0+wait_time*u.second, 
                location=self.observatory_location))

            command = -(np.cos(obj.az.rad)*np.cos(self.latitude*deg)/np.cos(obj.alt.rad))*SR / deg * wait_time

            time.sleep(wait_time-(self.observatory_time-t0).sec)

    def safety_status(self):
        '''Returns the status of the safety monitors'''
        safety_array = []
        if self.safety_monitor is not None:
            for safety_monitor in self.safety_monitor:
                safety_array.append(safety_monitor.IsSafe)
        return safety_array
    
    def switch_status(self):
        '''Returns the status of the switches'''
        switch_array = []
        if self.switch is not None:
            for switch in self.switch:
                temp = []
                for i in range(switch.MaxSwitch):
                    temp.append(switch.GetSwitch(i))
                switch_array.append(temp)
        return switch_array
    
    def run_autofocus(self, exposure=3, midpoint=0, nsteps=5, step_size=500, use_current_pointing=False):
        '''Runs the autofocus routine'''

        if self.autofocus is not None:
            logger.info('Using %s to run autofocus...' % self.autofocus_driver)
            result = self.autofocus.Run(exposure=exposure)
            logger.info('Autofocus routine completed.')
            return result
        elif self.focuser is not None:
            logger.info('Using observatory autofocus routine...')

            if not use_current_pointing:
                logger.info('Slewing to zenith...')
                self.slew_to_coordinates(obj=coord.SkyCoord(alt=90*u.deg, az=0*u.deg, frame='altaz'), 
                    control_dome=(self.dome is not None), control_rotator=(self.rotator is not None))
                logger.info('Slewing complete.')
            
            logger.info('Starting autofocus routine...')

            test_positions = np.linspace(midpoint-step_size*nsteps/2, midpoint+step_size*nsteps/2, nsteps)
            test_positions = np.round(test_positions, -2)

            focus_values = []
            for position, i in enumerate(test_positions):
                logger.info('Moving focuser to %s...' % position)
                if self.focuser.Absolute: self.focuser.Move(position)
                elif i == 0: self.focuser.Move(-position[0])
                else: self.focuser.Move(step_size)
                logger.info('Focuser moved.')
                
                logger.info('Taking %s second exposure...' % exposure)
                self.camera.StartExposure(exposure, True)
                while not image.ImageReady: time.sleep(0.1)
                logger.info('Exposure complete.')

                logger.info('Calculating mean star fwhm...')
                filename = tempfile.gettempdir() + '/autofocus.fts'
                self.save_last_image(filename, overwrite=True, do_wcs=True)
                cat = utils.get_image_source_catalog(filename)
                focus_values.append(np.mean(cat.fwhm))
                logger.info('FWHM = %.1f pixels' % focus_values[-1])
            
            popt, pcov = np.polyfit(test_positions, focus_values, 2)
            result = np.round(-popt[1]/(2*popt[0]), 0)
            logger.info('Best focus position is %i' % result)

            logger.info('Moving focuser to best focus position...')
            if self.focuser.Absolute: self.focuer.Move(result)
            else: self.focuser.Move(test_positions[-1]-result)
            logger.info('Focuser moved.')
            logger.info('Autofocus routine complete.')

            return result
        else:
            raise ObservatoryException('There is no focuser or autofocus driver present.')
    
    def recenter(self, obj=None, ra=None, dec=None, unit=('hr', 'deg'), frame='icrs', target_x_pixel=None, 
                target_y_pixel=None, initial_offset_dec=0, check_and_refine=True, max_attempts=5, tolerance=3, 
                exposure=10, readout=0, save_images=False, save_path='./', sync_mount=False, do_initial_slew=True):
        '''Attempts to place the requested right ascension and declination at the requested pixel location
        on the detector. 
        
        Parameters
        ----------
        obj : str or `~astropy.coordinates.SkyCoord`, optional
            The name of the target or a `~astropy.coordinates.SkyCoord` object of the target. If a string, 
            a query will be made to the SIMBAD database to get the coordinates. If a `~astropy.coordinates.SkyCoord`
            object, the coordinates will be used directly. If None, the ra and dec parameters must be specified.
        ra : `~astropy.coordinates.Longitude`-like, optional
            The ICRS J2000 right ascension of the target that will initialize a `~astropy.coordinates.SkyCoord` 
            object. This will override the ra value in the object parameter.
        dec : `~astropy.coordinates.Latitude`-like, optional
            The ICRS J2000 declination of the target that will initialize a `~astropy.coordinates.SkyCoord`
            object. This will override the dec value in the object parameter.
        unit : tuple, optional
            The units of the ra and dec parameters. Default is ('hr', 'deg').
        frame : str, optional
            The coordinate frame of the ra and dec parameters. Default is 'icrs'.
        target_x_pixel : float, optional
            The desired x pixel location of the target.
        target_y_pixel : float, optional
            The desired y pixel location of the target.
        initial_offset_dec : float, optional
            The initial offset of declination in arcseconds to use for the slew. Default is 0. Ignored if
            do_initial_slew is False.
        check_and_refine : bool, optional
            Whether or not to check the offset and refine the slew. Default is True.
        max_attempts : int, optional
            The maximum number of attempts to make to center the target. Default is 5. Ignored if
            check_and_refine is False.
        tolerance : float, optional
            The tolerance in pixels to consider the target centered. Default is 3. Ignored if
            check_and_refine is False.
        exposure : float, optional
            The exposure time in seconds to use for the centering images. Default is 10.
        save_images : bool, optional
            Whether or not to save the centering images. Default is False.
        save_path : str, optional
            The path to save the centering images to. Default is the current directory. Ignored if
            save_images is False.
        sync_mount : bool, optional
            Whether or not to sync the mount after the target is centered. Default is False. Note that
            if the target pixel location is not the center of the detector, the mount will be synced
            to this offset for all future slews.
        settle_time : float, optional
            The time in seconds to wait after the slew before checking the offset. Default is 5.
        do_initial_slew : bool, optional
            Whether or not to do the initial slew to the target. Default is True. If False, the current
            telescope position will be used as the starting point for the centering routine.

        Returns
        -------
        success : bool
            True if the target was successfully centered, False otherwise.
            '''

        obj = self._parse_obj_ra_dec(obj, ra, dec, unit, frame)

        logger.info('Attempting to put %s RA %i:%i:%.2f and Dec %i:%i:%.2f on pixel (%.2f, %.2f)' %
            (frame, obj.ra.hms[0], obj.ra.hms[1], obj.ra.hms[2], obj.dec.dms[0], obj.dec.dms[1], obj.dec.dms[2], 
            target_x_pixel, target_y_pixel))

        if initial_offset_dec != 0 and do_initial_slew:
            logger.info('Offseting the initial slew declination by %.2f arcseconds' % initial_offset_dec)

        for attempt in range(max_attempts):
            slew_obj = self.get_object_slew(obj)
            
            if check_and_refine:
                logger.info('Attempt %i of %i' % (attempt+1, max_attempts))
            
            if attempt == 0: 
                if do_initial_slew:
                    self.slew_to_coordinates(ra=slew_obj.ra.hour, dec=slew_obj.dec.deg + initial_offset_dec/3600, 
                        control_dome=(self.dome is not None), control_rotator=(self.rotator is not None))
            else: self.slew_to_coordinates(slew_obj.ra.hour, slew_obj.dec.deg, 
                    control_dome=(self.dome is not None), control_rotator=(self.rotator is not None))
            
            logger.info('Settling for %.2f seconds' % self.settle_time)
            time.sleep(self.settle_time)

            if not check_and_refine and attempt_number > 0:
                logger.info('Check and recenter is off, single-shot recentering complete')
                return True

            logger.info('Taking %.2f second exposure' % exposure)
            self.camera.ReadoutMode = self.camera.ReadoutModes[readout]
            self.camera.StartExposure(exposure, True)
            while not self.camera.ImageReady: time.sleep(0.1)
            logger.info('Exposure complete')

            temp_image = tempfile.gettempdir()+'%s.fts' % astrotime.Time(self.observatory_time, format='fits').value
            self.save_last_image(temp_image)

            logger.info('Searching for a WCS solution...')
            if type(self.wcs) is WCS:
                self.wcs.Solve(filename, ra_key='OBJCTRA', dec_key='OBJCTDEC', 
                    ra_dec_units=('hour', 'deg'), solve_timeout=60, 
                    scale_units='arcsecperpix', scale_type='ev',
                    scale_est=self.pixel_scale[0], scale_err=self.pixel_scale[0]*0.1,
                    parity=1, crpix_center=True)
            else: 
                for wcs, i in enumerate(self.wcs):
                    solution_found = wcs.Solve(filename, ra_key='OBJCTRA', dec_key='OBJCTDEC',
                        ra_dec_units=('hour', 'deg'), solve_timeout=60,
                        scale_units='arcsecperpix', scale_type='ev',
                        scale_est=self.pixel_scale[0], scale_err=self.pixel_scale[0]*0.1,
                        parity=1, crpix_center=True)
                    if solution_found: break

            if save_images:
                logger.info('Saving the centering image to %s' % save_path)
                shutil.copy(temp_image, save_path)

            if not solution_found:
                logger.warning('No WCS solution found, skipping this attempt')
                continue
            
            logger.info('WCS solution found, solving for the pixel location of the target')
            try:
                hdulist = fits.open(temp_image)
                w = astropy.wcs.WCS(hdulist[0].header)

                center_coord = w.pixel_to_world(int(self.camera.CameraXSize/2), int(self.camera.CameraYSize/2))
                center_ra = center_coord.ra.hour; center_dec = center_coord.dec.deg
                logger.debug('Center of the image is at RA %i:%i:%.2f and Dec %i:%i:%.2f' % 
                    (center_coord.ra.hms[0], center_coord.ra.hms[1], center_coord.ra.hms[2],
                    center_coord.dec.dms[0], center_coord.dec.dms[1], center_coord.dec.dms[2]))

                coord = w.pixel_to_world(target_x_pixel, target_y_pixel)
                target_pixel_ra = coord.ra.hour; target_pixel_dec = coord.dec.deg
                logger.debug('Target is at RA %i:%i:%.2f and Dec %i:%i:%.2f' % 
                (coord.ra.hms[0], coord.ra.hms[1], coord.ra.hms[2],
                coord.dec.dms[0], coord.dec.dms[1], coord.dec.dms[2]))

                pixels = w.world_to_pixel(obj)
                obj_x_pixel = pixels[0]; obj_y_pixel = pixels[1]
                logger.debug('Object is at pixel (%.2f, %.2f)' % (obj_x_pixel, obj_y_pixel))
            except: 
                logger.warning('Could not solve for the pixel location of the target, skipping this attempt')
                continue

            error_ra = obj.ra.hour - target_pixel_ra; error_dec = obj.dec.deg - target_pixel_dec
            error_x_pixels = obj_x_pixel - target_x_pixel; error_y_pixels = obj_y_pixel - target_y_pixel
            logger.debug('Error in RA is %.2f arcseconds' % (error_ra*15*3600))
            logger.debug('Error in Dec is %.2f arcseconds' % (error_dec*3600))
            logger.debug('Error in x pixels is %.2f' % error_x_pixels)
            logger.debug('Error in y pixels is %.2f' % error_y_pixels)

            if max(error_x_pixels, error_y_pixels) <= max_pixel_error:
                break

            logger.info('Offsetting next slew coordinates')
            obj = self._parse_obj_ra_dec(ra=obj.ra.hour + error_ra, dec=obj.dec.deg + error_dec, 
                                unit=('hour', 'deg'), frame='icrs')
        else:
            logger.warning('Target could not be centered after %d attempts' % max_attempts)
            return False
        
        if sync_mount:
                logger.info('Syncing the mount to the center ra and dec transformed to J-Now...')

                sync_obj = self._parse_obj_ra_dec(ra=center_ra, dec=center_dec, unit=('hour', 'deg'), frame='icrs')
                sync_obj = self.get_object_slew(sync_obj)
                self.telescope.SyncToCoordinates(sync_obj.ra.hour, sync_obj.dec.deg)
                logger.info('Sync complete')
            
        logger.info('Target is now in position after %d attempts' % (attempt+1))

        return True
    
    def take_flats(self, filter_exposure, filter_brightness=None, readouts=None, binnings=(1, 1), 
        repeat=10, save_path=None, new_folder=None, home_telescope=False, 
        final_telescope_position='no change'):
        '''Takes a sequence of flat frames'''

        logger.info('Taking flat frames')

        if self.filter_wheel is None or self.cover_calibrator is None:
            logger.warning('Filter wheel or cover calibrator is not available, exiting')
            return False

        if len(filter_exposure) != len(self.filters):
            logger.warn('Number of filter exposures does not match the number of filters, exiting')
            return False
        
        if save_path is None:
            save_path = os.getcwd()
            logger.debug('Setting save path to current working directory: %s' % save_path)
        
        if type(new_folder) is bool:
            save_path = os.path.join(save_path, datetime.datetime.now().strftime('Flats_%Y-%m-%d_%H-%M-%S'))
            os.makedirs(save_path)
            logger.info('Created new directory: %s' % save_path)
        elif type(new_folder) is str:
            save_path = os.path.join(save_path, new_folder)
            os.makedirs(save_path)
            logger.info('Created new directory: %s' % save_path)

        if home_telescope and self.telescope.CanFindHome:
            logger.info('Homing the telescope')
            self.telescope.FindHome()
            logger.info('Homing complete')

        logger.info('Slewing to point at cover calibrator')
        if self.telescope.CanSlewAltAz: 
            self.telescope.SlewToAltAz(self.cover_calibrator_az, self.cover_calibrator_alt)
        elif self.telescope.CanSlew: 
            obj = self.get_object_slew(obj=coord.AltAz(alt=self.cover_calibrator_alt, az=self.cover_calibrator_az, 
                obstime=self.observatory_time, location=self.observatory_location))
            self.telescope.SlewToCoordinates(obj.ra.hour, obj.dec.deg)
        self.telescope.Tracking = False
        logger.info('Slew complete')

        if self.cover_calibrator.CoverState != 'NotPresent':
            logger.info('Opening the cover calibrator')
            self.cover_calibrator.OpenCover()
            logger.info('Cover open')

        for i in range(len(self.filters)):
            if filter_exposure[i] == 0: continue
            for readout in readouts:
                self.camera.ReadoutMode = readout
                for binning in binnings:
                    if type(binnings[0]) is tuple: self.camera.BinX = binning[0]; self.camera.BinY = binning[1]
                    else: self.camera.BinX = binning; self.camera.BinY = binning
                    for j in range(repeat):
                        if self.camera.CanSetCCDTemperature:
                            while self.camera.CCDTemperature > (self.cooler_setpoint + self.cooler_tolerance):
                                logger.warning('Cooler is not at setpoint, waiting 10 seconds...')
                                time.sleep(10)
                        self.filter_wheel.Position = i
                        if self.cover_calibrator.CalibratorState != 'NotPresent' or filter_brightness is not None:
                            logger.info('Setting the cover calibrator brightness to %i' % filter_brightness[i])
                            self.cover_calibrator.CalibratorOn(filter_brightness[i]); logger.info('Cover calibrator on')
                        logger.info('Starting %s exposure' % self.filters[i])
                        camera.StartExposure(filter_exposure[i], False)
                        save_string = save_path + ('flat_%s_%ix%i_%4.4f_%i_%i.fts' % 
                            (self.filters[i], self.camera.BinX, self.camera.BinY, filter_exposure[i], 
                            self.camera.ReadoutModes[self.camera.ReadoutMode].replace(' ', ''), j))
                        while not camera.ImageReady:
                            time.sleep(0.1)
                        self.save_last_image(save_string, frametyp='Flat')
                        logger.info('Flat %i of %i complete' % (j, repeat))
                        logger.debug('Saved flat frame to %s' % save_string)
        
        if self.cover_calibrator.CalibratorState != 'NotPresent':
            logger.info('Turning off the cover calibrator')
            self.cover_calibrator.CalibratorOff()
            logger.info('Cover calibrator off')
            
        if self.cover_calibrator.CoverState != 'NotPresent':
            logger.info('Closing the cover calibrator')
            self.cover_calibrator.CloseCover()
            logger.info('Cover closed')

            if final_telescope_position == 'no change':
                logger.info('No change to telescope position requested, exiting')
            elif final_telescope_position == 'home' and self.telescope.CanFindHome:
                logger.info('Homing the telescope')
                self.telescope.FindHome()
                logger.info('Homing complete')
            elif final_telescope_position == 'park' and self.telescope.CanPark:
                logger.info('Parking the telescope')
                self.telescope.Park()
                logger.info('Parking complete')
            
        logger.info('Flats complete')

        return True
    
    def take_darks(self, exposures, readouts, binnings, repeat=10, save_path=None, new_folder=None):
        '''Takes a sequence of dark frames'''

        logger.info('Taking dark frames')

        if save_path is None:
            save_path = os.getcwd()
            logger.info('Setting save path to current working directory: %s' % save_path)
        
        if type(new_folder) is bool:
            save_path = os.path.join(save_path, datetime.datetime.now().strftime('Flats_%Y-%m-%d_%H-%M-%S'))
            os.makedirs(save_path)
            logger.info('Created new directory: %s' % save_path)
        elif type(new_folder) is str:
            save_path = os.path.join(save_path, new_folder)
            os.makedirs(save_path)
            logger.info('Created new directory: %s' % save_path)

        for exposure in exposures:
            for readout in readouts:
                self.camera.ReadoutMode = readout
                for binning in binnings:
                    if type(binnings[0]) is tuple: self.camera.BinX = binning[0]; self.camera.BinY = binning[1]
                    else: self.camera.BinX = binning; self.camera.BinY = binning
                    for j in range(repeat):
                        if self.camera.CanSetCCDTemperature:
                            while self.camera.CCDTemperature > (self.cooler_setpoint + self.cooler_tolerance):
                                logger.warning('Cooler is not at setpoint, waiting 10 seconds...')
                                time.sleep(10)
                        logger.info('Starting %4.4gs dark exposure' % exposure)
                        camera.StartExposure(exposure, False)
                        save_string = save_path + ('dark_%s_%ix%i_%4.4gs__%i.fts' % (
                                self.camera.ReadoutModes[self.camera.ReadoutMode].replace(' ', ''),
                                self.camera.BinX, self.camera.BinY, 
                                exposure, j))
                        while not camera.ImageReady:
                            time.sleep(0.1)
                        self.save_last_image(save_string, frametyp='Dark')
                        logger.info('Dark %i of %i complete' % (j, repeat))
                        logger.debug('Saved dark frame to %s' % save_string)
        
        logger.info('Darks complete')

        return True

    def save_config(self, filename):
        with open(filename, 'w') as configfile:
            self._config.write(configfile)
    
    def _parse_obj_ra_dec(self, obj=None, ra=None, dec=None, unit=('hour', 'deg'), frame='icrs', t=None):
        if type(obj) is str: 
            try: obj = coord.SkyCoord.from_name(obj)
            except: 
                try: 
                    if t is None: t = self.observatory_time
                    else: t = Time(t)
                    eph = MPC.get_ephemeris(obj, start=t, location=self.observatory_location, 
                        number=1, proper_motion='sky')
                    obj = coord.SkyCoord(ra=eph['RA'], dec=eph['Dec'], unit=('deg', 'deg'), pm_ra_cosdec=eph['dRA cos(Dec)'], pm_dec=eph['dDec'], frame='icrs')
                except:
                    try: obj = coord.get_body(obj, t, self.observatory_location)
                    except: raise ObservatoryException('The requested object could not be found using '+
                        'Sesame resolver, the Minor Planet Center Query, or the astropy.coordinates get_body function.')
        elif type(obj) is coord.SkyCoord: pass
        elif ra is not None and dec is not None: obj = coord.SkyCoord(ra=ra, 
            dec=dec, unit=unit, frame=frame)
        else: raise Exception('Either the object, the ra, or the dec must be specified.')

        return obj.transform_to('icrs')
    
    def _read_out_kwargs(self, dictionary):
        self.site_name = dictionary.get('site_name', self.site_name)
        self.instrument_name = dictionary.get('instrument_name', self.instrument_name)
        self.instrument_description = dictionary.get('instrument_description', self.instrument_description)
        self.get_site_from_telescope = dictionary.get('get_site_from_telescope', self.get_site_from_telescope)
        self.latitude = dictionary.get('latitude', self.latitude)
        self.longitude = dictionary.get('longitude', self.longitude)
        self.elevation = dictionary.get('elevation', self.elevation)
        self.get_optics_from_telescope = dictionary.get('get_optics_from_telescope', self.get_optics_from_telescope)
        self.diameter = dictionary.get('diameter', self.diameter)
        self.focal_length = dictionary.get('focal_length', self.focal_length)

        self.cooler_setpoint = dictionary.get('cooler_setpoint', self.cooler_setpoint)
        self.cooler_tolerance = dictionary.get('cooler_tolerance', self.cooler_tolerance)
        self.max_dimension = dictionary.get('max_dimension', self.max_dimension)

        self.cover_calibrator_alt = dictionary.get('cover_calibrator_alt', self.cover_calibrator_alt)
        self.cover_calibrator_az = dictionary.get('cover_calibrator_az', self.cover_calibrator_az)

        self.filters = dictionary.get('filters', self.filters)
        self.filter_focus_offsets = dictionary.get('filter_focus_offsets', self.filter_focus_offsets)

        self.focuser_max_error = dictionary.get('focuser_max_error', self.focuser_max_error)

        self.rotator_reverse = dictionary.get('rotator_reverse', self.rotator_reverse)
        self.rotator_min_angle = dictionary.get('rotator_min_angle', self.rotator_min_angle)
        self.rotator_max_angle = dictionary.get('rotator_max_angle', self.rotator_max_angle)

        self.min_altitude = dictionary.get('min_altitude', self.min_altitude)
        self.settle_time = dictionary.get('settle_time', self.settle_time)
    
    def _args_to_config(self, args):
        if args is None or len(args) == 0: return ''
        string = ''
        for arg in args:
            string += str(arg) + ' '
        return string[:-1]

    def _kwargs_to_config(self, kwargs):
        if kwargs is None or len(kwargs) == 0: return ''
        string = ''
        for key, value in kwargs.items():
            string += str(key) + ':' + str(value) + ' '
        return string[:-1]

    @property
    def autofocus_info(self):
        return {'Autofocus Driver': self.autofocus_driver}
    
    @property
    def camera_info(self):
        try: self.camera.Connected = True
        except: return {'CONNECT': (False, 'Camera connection')}
        info = {'CAMCON': (True, 'Camera connection'),
                'CAMREADY': (self.camera.ImageReady, 'Image ready'),
                'CAMSTATE': (['Idle', 'Waiting', 'Exposing', 'Reading', 
                                'Download', 'Error'][self.camera.CameraState], 'Camera state'),
                'PCNTCOMP': (None, 'Function percent completed'),
                'DATE-OBS': (None, 'YYYY-MM-DDThh:mm:ss observation start [UT]'),
                'JD': (None, 'Julian date'),
                'MJD': (None, 'Modified Julian date'),
                'EXPTIME': (None, 'Exposure time [seconds]'),
                'EXPOSURE': (None, 'Exposure time [seconds]'),
                'SUBEXP': (None, 'Subexposure time [seconds]'),
                'XBINNING': (self.camera.BinX, 'Image binning factor in width'),
                'YBINNING': (self.camera.BinY, 'Image binning factor in height'),
                'XORGSUBF': (self.camera.StartX, 'Subframe X position'),
                'YORGSUBF': (self.camera.StartY, 'Subframe Y position'),
                'XPOSSUBF': (self.camera.NumX, 'Subframe X dimension'),
                'YPOSSUBF': (self.camera.NumY, 'Subframe Y dimension'),
                'READOUT': (None, 'Image readout mode'),
                'READOUTM': (None, 'Image readout mode'),
                'FASTREAD': (None, 'Fast readout mode'),
                'GAIN': (None, 'Electronic gain'),
                'OFFSET': (None, 'Image offset'),
                'PULSGUID': (None, 'Pulse guiding'),
                'SENSTYP': (None, 'Sensor type'),
                'BAYERPAT': (None, 'Bayer color pattern'),
                'BAYOFFX': (None, 'Bayer X offset'),
                'BAYOFFY': (None, 'Bayer Y offset'),
                'HSINKT': (self.camera.HeatSinkTemperature, 'Heat sink temperature [C]'),
                'COOLERON': (None, 'Whether the cooler is on'),
                'COOLPOWR': (None, 'Cooler power in percent'),
                'SET-TEMP': (None, 'Camera temperature setpoint [C]'),
                'CCD-TEMP': (None, 'Camera temperature [C]'),
                'CMOS-TMP': (None, 'Camera temperature [C]'),
                'CAMNAME': (self.camera.Name, 'Name of camera'),
                'CAMERA': (self.camera.Name, 'Name of camera'),
                'CAMDRVER': (self.camera.DriverVersion, 'Camera driver version'),
                'CAMDRV': (self.camera.DriverInfo, 'Camera driver info'),
                'CAMINTF': (self.camera.InterfaceVersion, 'Camera interface version'),
                'CAMDESC': (self.camera.Description, 'Camera description'),
                'SENSOR': (self.camera.SensorName, 'Name of sensor'),
                'WIDTH': (self.camera.CameraXSize, 'Width of sensor in pixels'),
                'HEIGHT': (self.camera.CameraYSize, 'Height of sensor in pixels'),
                'XPIXSIZE': (self.camera.PixelSizeX, 'Pixel width in microns'),
                'YPIXSIZE': (self.camera.PixelSizeY, 'Pixel height in microns'),
                'MECHSHTR': (self.camera.HasShutter, 'Whether a camera mechanical shutter is present'),
                'ISSHUTTR': (self.camera.HasShutter, 'Whether a camera mechanical shutter is present'),
                'MINEXP': (self.camera.ExposureMin, 'Minimum exposure time [seconds]'),
                'MAXEXP': (self.camera.ExposureMax, 'Maximum exposure time [seconds]'),
                'EXPRESL': (self.camera.ExposureResolution, 'Exposure time resolution [seconds]'),
                'MAXBINSX': (self.camera.MaxBinX, 'Maximum binning factor in width'),
                'MAXBINSY': (self.camera.MaxBinY, 'Maximum binning factor in height'),
                'CANASBIN': (self.camera.CanAsymmetricBin, 'Can asymmetric bin'),
                'CANABRT': (self.camera.CanAbortExposure, 'Can abort exposures'),
                'CANSTP': (self.camera.CanStopExposure, 'Can stop exposures'),
                'CANCOOLP': (self.camera.CanGetCoolerPower, 'Can get cooler power'),
                'CANSETTE': (self.camera.CanSetCCDTemperature, 'Can camera set temperature'),
                'CANPULSE': (self.camera.CanPulseGuide, 'Can camera pulse guide'),
                'FULLWELL': (self.camera.FullWellCapacity, 'Full well capacity [e-]'),
                'MAXADU': (self.camera.MaxADU, 'Camera maximum ADU value possible'),
                'E-ADU': (self.camera.ElectronsPerADU, 'Gain [e- per ADU]'),
                'EGAIN': (self.camera.Gain, 'Electronic gain'),
                'CANFASTR': (self.camera.CanFastReadout, 'Can camera fast readout'),
                'READMDS': (None, 'Possible readout modes'),
                'GAINS': (None, 'Possible electronic gains'),
                'GAINMIN': (None, 'Minimum possible electronic gain'),
                'GAINMAX': (None, 'Maximum possible electronic gain'),
                'OFFSETS': (None, 'Possible offsets'),
                'OFFSETMN': (None, 'Minimum possible offset'),
                'OFFSETMX': (None, 'Maximum possible offset'),
                'CAMSUPAC': (self.camera.SupportedActions, 'Camera supported actions'),
                }
        try: info['Percent Completed'][0] = self.camera.PercentCompleted
        except: pass
        try: 
            info['DATE-OBS'][0] = self.camera.LastExposureStartTime
            info['JD'][0] = astrotime.Time(self.camera.LastExposureStartTime).jd
            info['MJD'][0] = astrotime.Time(self.camera.LastExposureStartTime).mjd
        except: pass
        try: 
            info['EXPTIME'][0] = self.camera.ExposureTime
            info['EXPOSURE'][0] = self.camera.ExposureTime
        except: pass
        try: info['SUBEXP'][0] = self.camera.SubExposureDuration
        except: pass
        info['CANFAST'][0] = self.camera.CanFastReadout
        if self.camera.CanFastReadout:
            info['READOUT'][0] = self.camera.ReadoutModes[self.camera.ReadoutMode]
            info['READOUTM'][0] = self.camera.ReadoutModes[self.camera.ReadoutMode]
            info['FASTREAD'][0] = self.camera.FastReadout
            info['READMDS'][0] = self.camera.ReadoutModes
            info['SENSTYP'][0] = ['Monochrome, Color, \
                RGGB, CMYG, CMYG2, LRGB'][self.camera.SensorType]
            if not self.camera.SensorType in (0, 1):
                info['BAYERPAT'][0] = self.camera.SensorType
                info['BAYOFFX'][0] = self.camera.BayerOffsetX
                info['BAYOFFY'][0] = self.camera.BayerOffsetY
        try: 
            info['GAINS'][0] = self.camera.Gains
            info['GAIN'][0] = self.camera.Gains[self.camera.Gain]
        except:
            try:
                info['GAINMIN'][0] = self.camera.GainMin
                info['GAINMAX'][0] = self.camera.GainMax
                info['GAIN'][0] = self.camera.Gain
            except: pass
        try:
            info['OFFSETS'][0] = self.camera.Offsets
            info['OFFSET'][0] = self.camera.Offsets[self.camera.Offset]
        except:
            try:
                info['OFFSETMN'][0] = self.camera.OffsetMin
                info['OFFSETMX'][0] = self.camera.OffsetMax
                info['OFFSET'][0] = self.camera.Offset
            except: pass
        info['CANPULSE'][0] = self.camera.CanPulseGuide
        if self.camera.CanPulseGuide:
            info['PULSGUID'][0] = self.camera.IsPulseGuiding
        try: info['COOLERON'][0] = self.camera.CoolerOn
        except: pass
        info['CANCOOLP'][0] = self.camera.CanGetCoolerPower
        if self.camera.CanGetCoolerPower:
            info['COOLPOWR'][0] = self.camera.CoolerPower
        info['CANSETTE'][0] = self.camera.CanSetCCDTemperature
        if self.camera.CanSetCCDTemperature:
            info['SET-TEMP'][0] = self.camera.SetCCDTemperature
        try: 
            info['CCD-TEMP'][0] = self.camera.CCDTemperature
            info['CMOS-TMP'][0] = self.camera.CMOSTemperature
        except: pass

        return info
    
    @property
    def cover_calibrator_info(self):
        if self.cover_calibrator is not None:
            try: self.cover_calibrator.Connected = True
            except: return {'CCALCONN': (False, 'Cover calibrator connected')}
            info = {'CCALCONN': (True, 'Cover calibrator connected'),
                    'CALSTATE': (self.cover_calibrator.CalibratorState, 'Calibrator state'),
                    'COVSTATE': (self.cover_calibrator.CoverState, 'Cover state'),
                    'BRIGHT': (None, 'Brightness of cover calibrator'),
                    'CCNAME': (self.cover_calibrator.Name, 'Cover calibrator name'),
                    'COVCAL': (self.cover_calibrator.Name, 'Cover calibrator name'),
                    'CCDRVER': (self.cover_calibrator.DriverVersion, 'Cover calibrator driver version'),
                    'CCDRV': (self.cover_calibrator.DriverInfo, 'Cover calibrator driver info'),
                    'CCINTF': (self.cover_calibrator.InterfaceVersion, 'Cover calibrator interface version'),
                    'CCDESC': (self.cover_calibrator.Description, 'Cover calibrator description'),
                    'MAXBRITE': (self.cover_calibrator.MaxBrightness, 'Cover calibrator maximum possible brightness'),
                    'CCSUPAC': (self.cover_calibrator.SupportedActions, 'Cover calibrator supported actions'),
                    }
            try: info['BRIGHT'][0] = self.cover_calibrator.Brightness
            except: pass
            return info
        else:
            return {'CCALCONN': (False, 'Cover calibrator connected')}
    
    @property
    def dome_info(self):
        if self.dome is not None:
            try: self.dome.Connected = True
            except: return {'DOMECONN': (False, 'Dome connected')}
            info = {'DOMECONN': (True, 'Dome connected'),
                    'DOMEALT': (None, 'Dome altitude [deg]'),
                    'DOMEAZ': (None, 'Dome azimuth [deg]'),
                    'DOMESHUT': (None, 'Dome shutter status'),
                    'DOMESLEW': (self.dome.Slewing, 'Dome slew status'),
                    'DOMESLAV': (None, 'Dome slave status'),
                    'DOMEHOME': (None, 'Dome home status'),
                    'DOMEPARK': (None, 'Dome park status'),
                    'DOMENAME': (self.dome.Name, 'Dome name'),
                    'DOMDRVER': (self.dome.DriverVersion, 'Dome driver version'),
                    'DOMEDRV': (self.dome.DriverInfo, 'Dome driver info'),
                    'DOMEINTF': (self.dome.InterfaceVersion, 'Dome interface version'),
                    'DOMEDESC': (self.dome.Description, 'Dome description'),
                    'DOMECALT': (self.dome.CanSetAltitude, 'Can dome set altitude'),
                    'DOMECAZ': (self.dome.CanSetAzimuth, 'Can dome set azimuth'),
                    'DOMECSHT': (self.dome.CanSetShutter, 'Can dome set shutter'),
                    'DOMECSLV': (self.dome.CanSlave, 'Can dome slave to mount'),
                    'DCANSYNC': (self.dome.CanSyncAzimuth, 'Can dome sync to azimuth value'),
                    'DCANHOME': (self.dome.CanFindHome, 'Can dome home'),
                    'DCANPARK': (self.dome.CanPark, 'Can dome park'),
                    'DCANSPRK': (self.dome.CanSetPark, 'Can dome set park'),
                    'DOMSUPAC': (self.dome.SupportedActions, 'Dome supported actions'),
                    }
            try: info['DOMEALT'][0] = self.dome.Altitude
            except: pass
            try: info['DOMEAZ'][0] = self.dome.Azimuth
            except: pass
            try: info['DOMESHUT'][0] = self.dome.ShutterStatus
            except: pass
            try: info['DOMESLAV'][0] = self.dome.Slaved
            except: pass
            try: info['DOMEHOME'][0] = self.dome.AtHome
            except: pass
            try: info['DOMEPARK'][0] = self.dome.AtPark
            except: pass
            return info
        else:
            return {'DOMECONN': (False, 'Dome connected')}

    @property
    def filter_wheel_info(self):
        if self.filter_wheel is not None:
            try: self.filter_wheel.Connected = True
            except: return {'FWCONN': (False, 'Filter wheel connected')}
            info = {'FWCONN': (True, 'Filter wheel connected'),
                    'FWPOS': (self.filter_wheel.Position, 'Filter wheel position'),
                    'FWNAME': (self.filter_wheel.Names[self.filter_wheel.Position], 'Filter wheel name (from filter wheel object configuration)'),
                    'FILTER': (self.filters[self.filter_wheel.Position], 'Filter name (from pyscope observatory object configuration)'),
                    'FOCOFFCG': (self.filter_wheel.FocusOffsets[self.filter_wheel.Position], 'Filter focus offset (from filter wheel object configuration)'),
                    'FWNAME': (self.filter_wheel.Name, 'Filter wheel name'),
                    'FWDRVER': (self.filter_wheel.DriverVersion, 'Filter wheel driver version'),
                    'FWDRV': (self.filter_wheel.DriverInfo, 'Filter wheel driver info'),
                    'FWINTF': (self.filter_wheel.InterfaceVersion, 'Filter wheel interface version'),
                    'FWDESC': (self.filter_wheel.Description, 'Filter wheel description'),
                    'FWALLNAM': (self.filter_wheel.Names, 'Filter wheel names'),
                    'FWALLOFF': (self.filter_wheel.FocusOffsets, 'Filter wheel focus offsets'),
                    'FWSUPAC': (self.filter_wheel.SupportedActions, 'Filter wheel supported actions'),
                    }
            return info
        else:
            return {'FWCONN': (False, 'Filter wheel connected')}

    @property
    def focuser_info(self):
        if self.focuser is not None:
            try: self.focuser.Connected = True
            except: return {'FOCCONN': (False, 'Focuser connected')}
            info = {'FOCCONN': (True, 'Focuser connected'),
                    'FOCPOS': (None, 'Focuser position'),
                    'FOCMOV': (self.focuser.IsMoving, 'Focuser moving'),
                    'TEMPCOMP': (None, 'Focuser temperature compensation'),
                    'FOCTEMP': (None, 'Focuser temperature'),
                    'FOCNAME': (self.focuser.Name, 'Focuser name'),
                    'FOCDRVER': (self.focuser.DriverVersion, 'Focuser driver version'),
                    'FOCDRV': (self.focuser.DriverInfo, 'Focuser driver info'),
                    'FOCINTF': (self.focuser.InterfaceVersion, 'Focuser interface version'),
                    'FOCDESC': (self.focuser.Description, 'Focuser description'),
                    'FOCSTEP': (None, 'Focuser step size'),
                    'FOCABSOL': (self.focuser.Absolute, 'Can focuser move to absolute position'),
                    'FOCMAXIN': (self.focuser.MaxIncrement, 'Focuser maximum increment'),
                    'FOCMAXST': (self.focuser.MaxStep, 'Focuser maximum step'),
                    'FOCTEMPC': (self.focuser.TempCompAvailable, 'Focuser temperature compensation available'),
                    }
            try: info['FOCPOS'][0] = self.focuser.Position
            except: pass
            try: info['TEMPCOMP'][0] = self.focuser.TempComp
            except: pass
            try: info['FOCTEMP'][0] = self.focuser.Temperature
            except: pass
            try: info['FOCSTEP'][0] = self.focuser.StepSize
            except: pass
            return info
        else:
            return {'FOCCONN': (False, 'Focuser connected')}
    
    @property
    def observatory_info(self):
        return {'OBSNAME': (self.site_name, 'Observatory name'),
                'OBSINSTN': (self.instrument_name, 'Instrument name'),
                'OBSINSTD': (self.instrument_description, 'Instrument description'),
                'OBSSITET': (self.get_site_from_telescope, 'Get site coordinates from telescope'),
                'OBSLAT': (self.latitude, 'Observatory latitude'),
                'OBSLONG': (self.longitude, 'Observatory longitude'),
                'OBSELEV': (self.elevation, 'Observatory altitude'),
                'OBSOPTTE': (self.get_optics_from_telescope, 'Get optics from telescope'),
                'OBSDIA': (self.diameter, 'Observatory diameter'),
                'OBSFL': (self.focal_length, 'Observatory focal length'),
                }

    @property
    def observing_conditions_info(self):
        if self.observing_conditions is not None:
            try: self.observing_conditions.Connected = True
            except: return {'WXCONN': (False, 'Observing conditions connected')}
            info = {'WXCONN': (True, 'Observing conditions connected'),
                    'WXAVGTIM': (self.observing_conditions.AveragePeriod, 'Observing conditions average period'),
                    'WXCLD': (None, 'Observing conditions cloud cover'),
                    'WXCLDUPD': (None, 'Observing conditions cloud cover last updated'),
                    'WCCLDD': (None, 'Observing conditions cloud cover sensor description'),
                    'WXDEW': (None, 'Observing conditions dew point'),
                    'WXDEWUPD': (None, 'Observing conditions dew point last updated'),
                    'WXDEWD': (None, 'Observing conditions dew point sensor description'),
                    'WXHUM': (None, 'Observing conditions humidity'),
                    'WXHUMUPD': (None, 'Observing conditions humidity last updated'),
                    'WXHUMD': (None, 'Observing conditions humidity sensor description'),
                    'WXPRES': (None, 'Observing conditions pressure'),
                    'WXPREUPD': (None, 'Observing conditions pressure last updated'),
                    'WXPRESD': (None, 'Observing conditions pressure sensor description'),
                    'WXRAIN': (None, 'Observing conditions rain rate'),
                    'WXRAIUPD': (None, 'Observing conditions rain rate last updated'),
                    'WXRAIND': (None, 'Observing conditions rain rate sensor description'),
                    'WXSKY': (None, 'Observing conditions sky brightness'),
                    'WXSKYUPD': (None, 'Observing conditions sky brightness last updated'),
                    'WXSKYD': (None, 'Observing conditions sky brightness sensor description'),
                    'WXSKYQ': (None, 'Observing conditions sky quality'),
                    'WXSKYQUP': (None, 'Observing conditions sky quality last updated'),
                    'WXSKYQD': (None, 'Observing conditions sky quality sensor description'),
                    'WXSKYTMP': (None, 'Observing conditions sky temperature'),
                    'WXSKTUPD': (None, 'Observing conditions sky temperature last updated'),
                    'WXSKTD': (None, 'Observing conditions sky temperature sensor description'),
                    'WXFWHM': (None, 'Observing conditions seeing'),
                    'WXFWHUP': (None, 'Observing conditions seeing last updated'),
                    'WXFWHMD': (None, 'Observing conditions seeing sensor description'),
                    'WXTEMP': (None, 'Observing conditions temperature'),
                    'WXTEMUPD': (None, 'Observing conditions temperature last updated'),
                    'WXTEMPD': (None, 'Observing conditions temperature sensor description'),
                    'WXWIND': (None, 'Observing conditions wind speed'),
                    'WXWINUPD': (None, 'Observing conditions wind speed last updated'),
                    'WXWINDD': (None, 'Observing conditions wind speed sensor description'),
                    'WXWINDIR': (None, 'Observing conditions wind direction'),
                    'WXWDIRUP': (None, 'Observing conditions wind direction last updated'),
                    'WXWDIRD': (None, 'Observing conditions wind direction sensor description'),
                    'WXWDGST': (None, 'Observing conditions wind gust over last two minutes'),
                    'WXWGDUPD': (None, 'Observing conditions wind gust last updated'),
                    'WXWGDSTD': (None, 'Observing conditions wind gust sensor description'),
                    'WXNAME': (self.observing_conditions.Name, 'Observing conditions name'),
                    'WXDRVER': (self.observing_conditions.DriverVersion, 'Observing conditions driver version'),
                    'WXDRIV': (self.observing_conditions.DriverInfo, 'Observing conditions driver info'),
                    'WXINTF': (self.observing_conditions.InterfaceVersion, 'Observing conditions interface version'),
                    'WXDESC': (self.observing_conditions.Description, 'Observing conditions description'),
                    }
            try: 
                info['WXCLD'][0] = self.observing_conditions.CloudCover
                info['WXCLDUPD'][0] = self.observing_conditions.TimeSinceLastUpdate('CloudCover')
                info['WXCLDD'][0] = self.observing_conditions.SensorDescription('CloudCover')
            except: pass
            try:
                info['WXDEW'][0] = self.observing_conditions.DewPoint
                info['WXDEWUPD'][0] = self.observing_conditions.TimeSinceLastUpdate('DewPoint')
                info['WXDEWD'][0] = self.observing_conditions.SensorDescription('DewPoint')
            except: pass
            try: 
                info['WXHUM'][0] = self.observing_conditions.Humidity
                info['WXHUMUPD'][0] = self.observing_conditions.TimeSinceLastUpdate('Humidity')
                info['WXHUMD'][0] = self.observing_conditions.SensorDescription('Humidity')
            except: pass
            try:
                info['WXPRES'][0] = self.observing_conditions.Pressure
                info['WXPREUPD'][0] = self.observing_conditions.TimeSinceLastUpdate('Pressure')
                info['WXPRESD'][0] = self.observing_conditions.SensorDescription('Pressure')
            except: pass
            try:
                info['WXRAIN'][0] = self.observing_conditions.RainRate
                info['WXRAIUPD'][0] = self.observing_conditions.TimeSinceLastUpdate('RainRate')
                info['WXRAIND'][0] = self.observing_conditions.SensorDescription('RainRate')
            except: pass
            try:
                info['WXSKY'][0] = self.observing_conditions.SkyBrightness
                info['WXSKYUPD'][0] = self.observing_conditions.TimeSinceLastUpdate('SkyBrightness')
                info['WXSKYD'][0] = self.observing_conditions.SensorDescription('SkyBrightness')
            except: pass
            try: 
                info['WXSKYQ'][0] = self.observing_conditions.SkyQuality
                info['WXSKYQUP'][0] = self.observing_conditions.TimeSinceLastUpdate('SkyQuality')
                info['WXSKYQD'][0] = self.observing_conditions.SensorDescription('SkyQuality')
            except: pass
            try:
                info['WXSKYTMP'][0] = self.observing_conditions.SkyTemperature
                info['WXSKTUPD'][0] = self.observing_conditions.TimeSinceLastUpdate('SkyTemperature')
                info['WXSKTD'][0] = self.observing_conditions.SensorDescription('SkyTemperature')
            except: pass
            try:
                info['WXFWHM'][0] = self.observing_conditions.Seeing
                info['WXFWHUP'][0] = self.observing_conditions.TimeSinceLastUpdate('Seeing')
                info['WXFWHMD'][0] = self.observing_conditions.SensorDescription('Seeing')
            except: pass
            try:
                info['WXTEMP'][0] = self.observing_conditions.Temperature
                info['WXTEMUPD'][0] = self.observing_conditions.TimeSinceLastUpdate('Temperature')
                info['WXTEMPD'][0] = self.observing_conditions.SensorDescription('Temperature')
            except: pass
            try:
                info['WXWIND'][0] = self.observing_conditions.WindSpeed
                info['WXWINUPD'][0] = self.observing_conditions.TimeSinceLastUpdate('WindSpeed')
                info['WXWINDD'][0] = self.observing_conditions.SensorDescription('WindSpeed')
            except: pass
            try:
                info['WXWINDIR'][0] = self.observing_conditions.WindDirection
                info['WXWDIRUP'][0] = self.observing_conditions.TimeSinceLastUpdate('WindDirection')
                info['WXWDIRD'][0] = self.observing_conditions.SensorDescription('WindDirection')
            except: pass
            try:
                info['WXWDGST'][0] = self.observing_conditions.WindGust
                info['WXWGDUPD'][0] = self.observing_conditions.TimeSinceLastUpdate('WindGust')
                info['WXWGDSTD'][0] = self.observing_conditions.SensorDescription('WindGust')
            except: pass
            return info
        else:
            return {'WXCONN': (False, 'Observing conditions connected')}

    @property
    def rotator_info(self):
        if self.rotator is not None:
            try: self.rotator.Connected = True
            except: return {'ROTCONN': (False, 'Rotator connected')}
            info = {'ROTCONN': (True, 'Rotator connected'),
                    'ROTPOS': (self.rotator.Position, 'Rotator position'),
                    'ROTMECHP': (self.rotator.MechanicalPosition, 'Rotator mechanical position'),
                    'ROTTARGP': (self.rotator.TargetPosition, 'Rotator target position'),
                    'ROTMOV': (self.rotator.IsMoving, 'Rotator moving'),
                    'ROTREVSE': (self.rotator.Reverse, 'Rotator reverse'),
                    'ROTNAME': (self.rotator.Name, 'Rotator name'),
                    'ROTDRVER': (self.rotator.DriverVersion, 'Rotator driver version'),
                    'ROTDRV': (self.rotator.DriverInfo, 'Rotator driver name'),
                    'ROTINTFC': (self.rotator.InterfaceVersion, 'Rotator interface version'),
                    'ROTDESC': (self.rotator.Description, 'Rotator description'),
                    'ROTSTEP': (None, 'Rotator step size [degrees]'),
                    'ROTCANRV': (self.rotator.CanReverse, 'Can rotator reverse'),
                    'ROTSUPAC': (self.rotator.SupportedActions, 'Rotator supported actions'),
                    }
            try: info['ROTSTEP'][0] = self.rotator.StepSize
            except: pass
            return info
        else:
            return {'ROTCONN': (False, 'Rotator connected')}
    
    @property
    def safety_monitor_info(self, index=None):
        if self.safety_monitor is not None:
            all_info = []
            for i in range(len(self.safety_monitor)):
                try: self.safety_monitor[i].Connected = True
                except: info = {'SM%iCONN' % i: (False, 'Safety monitor connected')}
                info = {('SM%iCONN' % i): (True, 'Safety monitor connected'),
                        ('SM%iISSAF' % i): (self.safety_monitor[i].IsSafe, 'Safety monitor safe'),
                        ('SM%iNAME' % i): (self.safety_monitor[i].Name, 'Safety monitor name'),
                        ('SM%iDRVER' % i): (self.safety_monitor[i].DriverVersion, 'Safety monitor driver version'),
                        ('SM%iDRV' % i): (self.safety_monitor[i].DriverInfo, 'Safety monitor driver name'),
                        ('SM%iINTF' % i): (self.safety_monitor[i].InterfaceVersion, 'Safety monitor interface version'),
                        ('SM%iDESC' % i): (self.safety_monitor[i].Description, 'Safety monitor description'),
                        ('SM%iSUPAC' % i): (self.safety_monitor[i].SupportedActions, 'Safety monitor supported actions'),
                        }
                all_info.append(info)
        else: 
            return {'SM0CONN': (False, 'Safety monitor connected')}
        
        if index is not None: return all_info[index]
        elif len(all_info) == 1: return all_info[0]
        else: return all_info
    
    @property
    def switch_info(self, index=None):
        if self.switch is not None:
            all_info = []
            for i in range(len(self.switch)):
                try: self.switch.Connected = True
                except: info = {('SW%iCONN' % i): (False, 'Switch connected')}
                info = {('SW%iCONN' %i): (True, 'Switch connected'),
                        ('SW%iNAME' %i): (self.switch[i].Name, 'Switch name'),
                        ('SW%iDRVER' %i): (self.switch[i].DriverVersion, 'Switch driver version'),
                        ('SW%iDRV' %i): (self.switch[i].DriverInfo, 'Switch driver name'),
                        ('SW%iINTF' %i): (self.switch[i].InterfaceVersion, 'Switch interface version'),
                        ('SW%iDESC' %i): (self.switch[i].Description, 'Switch description'),
                        ('SW%iSUPAC' %i): (self.switch[i].SupportedActions, 'Switch supported actions'),
                        ('SW%iMAXSW' %i): (self.switch[i].MaxSwitch, 'Switch maximum switch'),
                        }
                for j in range(self.switch[i].MaxSwitch):
                    info[('SW%iSW%iNM' % (i, j))] = (self.switch[i].GetSwitchName(j), 'Switch %i Device %i name' % (i, j))
                    info[('SW%iSW%iDS' % (i, j))] = (self.switch[i].GetSwitchDescription(j), 'Switch %i Device %i description' % (i, j))
                    info[('SW%iSW%i' % (i, j))] = (self.switch[i].GetSwitch(j), 'Switch %i Device %i state' % (i, j))
                    info[('SW%iSW%iVA' % (i, j))] = (self.switch[i].GetSwitchValue(j), 'Switch %i Device %i value' % (i, j))
                    info[('SW%iSW%iMN' % (i, j))] = (self.switch[i].MinSwitchValue(j), 'Switch %i Device %i minimum value' % (i, j))
                    info[('SW%iSW%iMX' % (i, j))] = (self.switch[i].MaxSwitchValue(j), 'Switch %i Device %i maximum value' % (i, j))
                    info[('SW%iSW%iST' % (i, j))] = (self.switch[i].SwitchStep(j), 'Switch %i Device %i step' % (i, j))

                all_info.append(info)
        else:
            return {'SW0CONN': (False, 'Switch connected')}

        if index is not None: return all_info[index]
        elif len(all_info) == 1: return all_info[0]
        else: return all_info
    
    @property
    def telescope_info(self):
        try: self.telescope.Connected = True
        except: return {'TELCONN': (False, 'Telescope connected')}
        info = {'TELCONN': (True, 'Telescope connected'),
                'TELHOME': (self.telescope.AtHome, 'Is telescope at home position'),
                'TELPARK': (self.telescope.AtPark, 'Is telescope at park position'),
                'TELALT': (None, 'Telescope altitude [degrees]'),
                'TELAZ': (None, 'Telescope azimuth North-referenced positive East (clockwise) [degrees]'),
                'TELRA': (self.telescope.RightAscension, 'Telescope right ascension in TELEQSYS coordinate frame [hours]'),
                'TELDEC': (self.telescope.Declination, 'Telescope declination in TELEQSYS coordinate frame [degrees]'),
                'TARGRA': (None, 'Target right ascension in EQSYS coordinate frame [hours]'),
                'TARGDEC': (None, 'Target declination in EQSYS coordinate frame [degrees]'),
                'OBJCTRA': (None, 'Object right ascension in ICRS coordinate frame [hours]'),
                'OBJCTDEC': (None, 'Object declination in ICRS coordinate frame [degrees]'),
                'OBJCTALT': (None, 'Object altitude [degrees]'),
                'OBJCTAZ': (None, 'Object azimuth North-referenced positive East (clockwise) [degrees]'),
                'OBJCTHA': (None, 'Object hour angle [hours]'),
                'AIRMASS': (None, 'Airmass'),
                'MOONANGL': (None, 'Angle between object and moon [degrees]'),
                'MOONPHAS': (None, 'Moon phase [percent]'),
                'TELSLEW': (None, 'Is telescope slewing'),
                'TELSETT': (None, 'Telescope settling time [seconds]'),
                'TELPIER': (None, 'Telescope pier side'),
                'TELTRACK': (None, 'Is telescope tracking'),
                'TELTRKRT': (None, 'Telescope tracking rate (sidereal)'),
                'TELOFFRA': (None, 'Telescope RA tracking offset [seconds per sidereal second]'),
                'TELOFFDC': (None, 'Telescope DEC tracking offset [arcseconds per sidereal second]'),
                'TELPULSE': (None, 'Is telescope pulse guiding'),
                'TELGUIDR': (None, 'Telescope pulse guiding RA rate [degrees/sec]'),
                'TELGUIDD': (None, 'Telescope pulse guiding DEC rate [arcseconds/sec]'),
                'TELDOREF': (None, 'Does telescope do refraction'),
                'TELLST': (self.telescope.SiderealTime, 'Telescope local sidereal time [hours]'),
                'TELUT': (None, 'Telescope UTC date'),
                'TELNAME': (self.telescope.Name, 'Telescope name'),
                'TELDRVER': (self.telescope.DriverVersion, 'Telescope driver version'),
                'TELDRV': (self.telescope.DriverInfo, 'Telescope driver name'),
                'TELINTF': (self.telescope.InterfaceVersion, 'Telescope interface version'),
                'TELDESC': (self.telescope.Description, 'Telescope description'),
                'TELAPAR': (None, 'Telescope aperture area [m^2]'),
                'TELDIAM': (None, 'Telescope aperture diameter [m]'),
                'TELFOCL': (None, 'Telescope focal length [m]'),
                'TELELEV': (None, 'Telescope elevation [degrees]'), 
                'TELLAT': (None, 'Telescope latitude [degrees]'),
                'TELLONG': (None, 'Telescope longitude [degrees]'),
                'TELALN': (None, 'Telescope alignment mode'),
                'TELEQSYS': (['equOther', 'equTopocentric', 'equJ2000', 'equJ2050', 'equB1950'][self.telescope.EquatorialSystem], 'Telescope equatorial coordinate system'),
                'TELCANHM': (self.telescope.CanFindHome, 'Can telescope find home'),
                'TELCANPA': (self.telescope.CanPark, 'Can telescope park'),
                'TELCANUN': (self.telescope.CanUnpark, 'Can telescope unpark'),
                'TELCANPP': (self.telescope.CanSetPark, 'Can telescope set park position'),
                'TELCANPG': (self.telescope.CanPulseGuide, 'Can telescope pulse guide'),
                'TELCANGR': (self.telescope.CanSetGuideRates, 'Can telescope set guide rates'),
                'TELCANTR': (self.telescope.CanSetTracking, 'Can telescope set tracking'),
                'TELCANSR': (self.telescope.CanSetRightAscensionRate, 'Can telescope set RA offset rate'),
                'TELCANSD': (self.telescope.CanSetDeclinationRate, 'Can telescope set DEC offset rate'),
                'TELCANSP': (self.telescope.CanSetPierSide, 'Can telescope set pier side'),
                'TELCANSL': (self.telescope.CanSlew, 'Can telescope slew to equatorial coordinates'),
                'TELCNSLA': (self.telescope.CanSlewAsync, 'Can telescope slew asynchronously'),
                'TELCANSF': (self.telescope.CanSlewAltAz, 'Can telescope slew to alt-azimuth coordinates'),
                'TELCNSFA': (self.telescope.CanSlewAltAzAsync, 'Can telescope slew to alt-azimuth coordinates asynchronously'),
                'TELCANSY': (self.telescope.CanSync, 'Can telescope sync to equatorial coordinates'),
                'TELCNSYA': (self.telescope.CanSyncAltAz, 'Can telescope sync to alt-azimuth coordinates'),
                'TELTRCKS': (self.telescope.TrackingRates, 'Telescope tracking rates'),
                'TELSUPAC': (self.telescope.SupportedActions, 'Telescope supported actions'),
                }
        try: info['TELALT'][0] = self.telescope.Altitude
        except: pass
        try: info['TELAZ'][0] = self.telescope.Azimuth
        except: pass
        try: info['TARGRA'][0] = self.telescope.TargetRightAscension
        except: pass
        try: info['TARGDEC'][0] = self.telescope.TargetDeclination
        except: pass
        obj = self.get_current_object()
        info['OBJCTRA'][0] = obj.ra.to_string(unit=u.hour)
        info['OBJCTDEC'][0] = obj.dec.to_string(unit=u.degree)
        info['OBJCTALT'][0] = obj.transform_to(coord.AltAz(obstime=self.observatory_time, location=self.observatory_location)).alt.to(u.degree)
        info['OBJCTAZ'][0] = obj.transform_to(coord.AltAz(obstime=self.observatory_time, location=self.observatory_location)).az.to(u.degree)
        info['OBJCTHA'][0] = abs(self.lst - obj.ra).to(u.hour)
        info['AIRMASS'][0] = utils.airmass(obj.transform_to(coord.AltAz(obstime=self.observatory_time, location=self.observatory_location)).alt.to(u.rad))
        info['MOONANGL'][0] = coord.get_moon(self.observatory_time, location=self.observatory_location).separation(obj).to(u.degree)
        info['MOONPHAS'][0] = self.moon_illumination(self.observatory_time)
        try: info['TELSLEW'][0] = self.telescope.Slewing
        except: pass
        try: info['TELSETT'][0] = self.telescope.SlewSettleTime
        except: pass
        try: info['TELPIER'][0] = ['pierEast', 'pierWest', 'pierUnknown'][self.telescope.SideOfPier]
        except: pass
        try: info['TELTRACK'][0] = self.telescope.Tracking
        except: pass
        try: info['TELTRKRT'][0] = self.telescope.TrackingRates[self.telescope.TrackingRate]
        except: pass
        try: info['TELOFFRA'][0] = self.telescope.RightAscensionRate
        except: pass
        try: info['TELOFFDC'][0] = self.telescope.DeclinationRate
        except: pass
        try: info['TELPULSE'][0] = self.telescope.IsPulseGuiding
        except: pass
        try: info['TELGUIDR'][0] = self.telescope.GuideRateRightAscension
        except: pass
        try: info['TELGUIDD'][0] = self.telescope.GuideRateDeclination
        except: pass
        try: info['TELDOREF'][0] = self.telescope.DoesRefraction
        except: pass
        try: info['TELUT'][0] = self.telescope.UTCDate
        except: pass
        try: info['TELAPAR'][0] = self.telescope.ApertureArea
        except: pass
        try: info['TELDIAM'][0] = self.telescope.ApertureDiameter
        except: pass
        try: info['TELFOCL'][0] = self.telescope.FocalLength
        except: pass
        try: info['TELELEV'][0] = self.telescope.SiteElevation
        except: pass
        try: info['TELLAT'][0] = self.telescope.SiteLatitude
        except: pass
        try: info['TELLONG'][0] = self.telescope.SiteLongitude
        except: pass
        try: info['TELALN'][0] = ['AltAz', 'Polar', 'GermanPolar'][self.telescope.AlignmentMode]
        except: pass
        return info
    
    @property
    def threads_info(self):
        return {'DEROTATE': (not self.derotation_thread is None, 'Is derotation thread active'),
                'OCTHREAD': (not self.observing_conditions_thread is None, 'Is observing conditions thread active'),
                'SMTHREAD': (not self.safety_monitor_thread is None, 'Is status monitor thread active'),
                }
    
    @property
    def wcs_info(self):
        return {'WCSDRV': (self.wcs_driver, 'WCS driver')}

    @property
    def observatory_location(self):
        '''Returns the EarthLocation object for the observatory'''
        return coord.EarthLocation(lat=self.latitude, lon=self.longitude, height=self.elevation)

    @property
    def observatory_time(self):
        '''Returns the current observatory time'''
        return astrotime.Time.now()

    @property
    def plate_scale(self):
        '''Returns the plate scale of the telescope in arcsec/mm'''
        return 206265/self.focal_length
    
    @property
    def pixel_scale(self):
        '''Returns the pixel scale of the camera'''
        return (self.plate_scale * self.camera.PixelSizeX*1e-3, self.plate_scale * self.camera.PixelSizeY*1e-3)

    @property
    def site_name(self):
        return self._site_name
    @site_name.setter
    def site_name(self, value):
        self._site_name = value if value is not None or value !='' else None
        self._config['site']['site_name'] = self._site_name if self._site_name is not None else ''
    
    @property
    def instrument_name(self):
        return self._instrument_name
    @instrument_name.setter
    def instrument_name(self, value):
        self._instrument_name = value if value is not None or value !='' else None
        self._config['site']['instrument_name'] = self._instrument_name if self._instrument_name is not None else ''
    
    @property
    def instrument_description(self):
        return self._instrument_description
    @instrument_description.setter
    def instrument_description(self, value):
        self._instrument_description = value if value is not None or value !='' else None
        self._config['site']['instrument_description'] = self._instrument_description if self._instrument_description is not None else ''

    @property
    def get_site_from_telescope(self):
        return self._get_site_from_telescope
    @get_site_from_telescope.setter
    def get_site_from_telescope(self, value):
        self._get_site_from_telescope = bool(value)
        self._config['site']['get_site_from_telescope'] = str(self._get_site_from_telescope)
        if self._get_site_from_telescope:
            self.latitude = self.telescope.SiteLatitude
            self.longitude = self.telescope.SiteLongitude
            self.elevation = self.telescope.SiteElevation
        
    @property
    def latitude(self):
        return self._latitude
    @latitude.setter
    def latitude(self, value):
        if self.get_site_from_telescope: raise ObservatoryException('Cannot set latitude when get_site_from_telescope is True')
        self._latitude = coord.Latitude(value) if value is not None or value !='' else None
        self._config['site']['latitude'] = self._latitude.to_string(unit=coord.units.degree, sep=':', precision=2, 
            pad=True, alwayssign=True, decimal=True) if self._latitude is not None else ''
    
    @property
    def longitude(self):
        return self._longitude
    @longitude.setter
    def longitude(self, value):
        if self._get_site_from_telescope: raise ObservatoryException('Cannot set longitude when get_site_from_telescope is True')
        self._longitude = coord.Longitude(value) if value is not None or value !='' else None
        self._config['site']['longitude'] = self._longitude.to_string(unit=coord.units.degree, sep=':', precision=2, 
            pad=True, alwayssign=True, decimal=True) if self._longitude is not None else ''
    
    @property
    def elevation(self):
        return self._elevation
    @elevation.setter
    def elevation(self, value):
        if self._get_site_from_telescope: raise ObservatoryException('Cannot set elevation when get_site_from_telescope is True')
        self._elevation = max(float(value), 0) if value is not None or value !='' else None
        self._config['site']['elevation'] = str(self._elevation) if self._elevation is not None else ''
    
    @property
    def get_optics_from_telescope(self):
        return self._get_optics_from_telescope
    @get_optics_from_telescope.setter
    def get_optics_from_telescope(self, value):
        self._get_optics_from_telescope = bool(value)
        self._config['site']['get_optics_from_telescope'] = str(self._get_optics_from_telescope)
        if self._get_optics_from_telescope:
            self.diameter = self.telescope.ApertureDiameter
            self.focal_length = self.telescope.FocalLength

    @property
    def diameter(self):
        return self._diameter
    @diameter.setter
    def diameter(self, value):
        if self._get_optics_from_telescope: raise ObservatoryException('Cannot set diameter when get_optics_from_telescope is True')
        self._diameter = max(float(value), 0) if value is not None or value !='' else None
        self._config['site']['diameter'] = str(self._diameter) if self._diameter is not None else ''
    
    @property
    def focal_length(self):
        return self._focal_length
    @focal_length.setter
    def focal_length(self, value):
        if self._get_optics_from_telescope: raise ObservatoryException('Cannot set focal_length when get_optics_from_telescope is True')
        self._focal_length = max(float(value), 0) if value is not None or value !='' else None
        self._config['site']['focal_length'] = str(self._focal_length) if self._focal_length is not None else ''
    
    @property
    def camera(self):
        return self._camera

    @property
    def camera_driver(self):
        return self._camera_driver
    
    @property
    def camera_ascom(self):
        return self._camera_ascom

    @property
    def cooler_setpoint(self):
        return self._cooler_setpoint
    @cooler_setpoint.setter
    def cooler_setpoint(self, value):
        self._cooler_setpoint = max(float(value), -273.15) if value is not None or value !='' else None
        self._config['camera']['cooler_setpoint'] = str(self._cooler_setpoint) if self._cooler_setpoint is not None else ''
        if self.camera.CanSetCCDTemperature and self._cooler_setpoint is not None: 
            self.camera.SetCCDTemperature = self._cooler_setpoint
        else: raise ObservatoryException('Camera does not support setting the CCD temperature')
    
    @property
    def cooler_tolerance(self):
        return self._cooler_tolerance
    @cooler_tolerance.setter
    def cooler_tolerance(self, value):
        self._cooler_tolerance = max(float(value), 0) if value is not None or value !='' else None
        self._config['camera']['cooler_tolerance'] = str(self._cooler_tolerance) if self._cooler_tolerance is not None else ''
    
    @property
    def max_dimension(self):
        return self._max_dimension
    @max_dimension.setter
    def max_dimension(self, value):
        self._max_dimension = max(int(value), 1) if value is not None or value !='' else None
        self._config['camera']['max_dimension'] = str(self._max_dimension) if self._max_dimension is not None else ''
        if self._max_dimension is not None and max(self.camera.CameraXSize, self.camera.CameraYSize) > self._max_dimension:
            raise ObservatoryException('Camera sensor size exceeds maximum dimension of %d' % self._max_dimension)

    @property
    def cover_calibrator(self):
        return self._cover_calibrator
    
    @property
    def cover_calibrator_driver(self):
        return self._cover_calibrator_driver

    @property
    def cover_calibrator_ascom(self):
        return self._cover_calibrator_ascom
    
    @property
    def cover_calibrator_alt(self):
        return self._cover_calibrator_alt
    @cover_calibrator_alt.setter
    def cover_calibrator_alt(self, value):
        self._cover_calibrator_alt = min(max(float(value), 0), 90) if value is not None or value !='' else None
        self._config['cover_calibrator']['cover_calibrator_alt'] = str(self._cover_calibrator_alt) if self._cover_calibrator_alt is not None else ''
    
    @property
    def cover_calibrator_az(self):
        return self._cover_calibrator_az
    @cover_calibrator_az.setter
    def cover_calibrator_az(self, value):
        self._cover_calibrator_az = min(max(float(value), 0), 360) if value is not None or value !='' else None
        self._config['cover_calibrator']['cover_calibrator_az'] = str(self._cover_calibrator_az) if self._cover_calibrator_az is not None else ''

    @property
    def dome(self):
        return self._dome

    @property
    def dome_driver(self):
        return self._dome_driver
    
    @property
    def dome_ascom(self):
        return self._dome_ascom

    @property
    def filter_wheel(self):
        return self._filter_wheel
    
    @property
    def filter_wheel_driver(self):
        return self._filter_wheel_driver
    
    @property
    def filter_wheel_ascom(self):
        return self._filter_wheel_ascom

    @property
    def filters(self):
        return self._filters
    @filters.setter
    def filters(self, value, position=None):
        if position is None: self._filters = list(value) if value is not None or value !='' else None
        else: self._filters[position] = char(value) if value is not None or value !='' else None
        self._config['filter_wheel']['filters'] = ', '.join(self._filters) if self._filters is not None else ''

    @property
    def filter_focus_offsets(self):
        return self._filter_focus_offsets
    @filter_focus_offsets.setter
    def filter_focus_offsets(self, value, filt=None):
        if filt is None: self._filter_focus_offsets = dict(zip(self.filters, value)) if value is not None or value !='' else None
        else: self._filter_focus_offsets[filt] = float(value) if value is not None or value !='' else None
        self._config['filter_wheel']['filter_focus_offsets'] = ', '.join(self._filter_focus_offsets.values()) if self._filter_focus_offsets is not None else ''
    
    @property
    def focuser(self):
        return self._focuser
    
    @property
    def focuser_driver(self):
        return self._focuser_driver
    
    @property
    def focuser_ascom(self):
        return self._focuser_ascom
    
    @property
    def focuser_max_error(self):
        return self._focuser_max_error
    @focuser_max_error.setter
    def focuser_max_error(self, value):
        self._focuser_max_error = max(float(value), 0) if value is not None or value !='' else None
        self._config['focuser']['focuser_max_error'] = str(self._focuser_max_error) if self._focuser_max_error is not None else ''

    @property
    def observing_conditions(self):
        return self._observing_conditions
    
    @property
    def observing_conditions_driver(self):
        return self._observing_conditions_driver

    @property
    def observing_conditions_ascom(self):
        return self._observing_conditions_ascom

    @property
    def rotator(self):
        return self._rotator
    
    @property 
    def rotator_driver(self):
        return self._rotator_driver

    @property
    def rotator_ascom(self):
        return self._rotator_ascom
    
    @property
    def rotator_reverse(self):
        return self._rotator_reverse
    @rotator_reverse.setter
    def rotator_reverse(self, value):
        self._rotator_reverse = bool(value) if value is not None or value !='' else None
        self._config['rotator']['rotator_reverse'] = str(self._rotator_reverse) if self._rotator_reverse is not None else ''
        self.rotator.Reverse = self._rotator_reverse
    
    @property
    def rotator_min_angle(self):
        return self._rotator_min_angle
    @rotator_min_angle.setter
    def rotator_min_angle(self, value):
        self._rotator_min_angle = float(value) if value is not None or value !='' else None
        self._config['rotator']['rotator_min_angle'] = str(self._rotator_min_angle) if self._rotator_min_angle is not None else ''
    
    @property
    def rotator_max_angle(self):
        return self._rotator_max_angle
    @rotator_max_angle.setter
    def rotator_max_angle(self, value):
        self._rotator_max_angle = float(value) if value is not None or value !='' else None
        self._config['rotator']['rotator_max_angle'] = str(self._rotator_max_angle) if self._rotator_max_angle is not None else ''

    @property
    def safety_monitor(self):
        return self._safety_monitor
    
    @property
    def safety_monitor_driver(self):
        return self._safety_monitor_driver
    
    @property
    def safety_monitor_ascom(self):
        return self._safety_monitor_ascom
    
    @property
    def switch(self):
        return self._switch

    @property
    def switch_driver(self):
        return self._switch_driver
    
    @property
    def switch_ascom(self):
        return self._switch_ascom
    
    @property
    def telescope(self):
        return self._telescope
    
    @property
    def telescope_driver(self):
        return self._telescope_driver
    
    @property
    def telescope_ascom(self):
        return self._telescope_ascom

    @property
    def min_altitude(self):
        return self._min_altitude
    @min_altitude.setter
    def min_altitude(self, value):
        self._min_altitude = min(max(float(value), 0), 90) if value is not None or value !='' else None
        self._config['telescope']['min_altitude'] = str(self._min_altitude) if self._min_altitude is not None else ''
    
    @property
    def settle_time(self):
        return self._settle_time
    @settle_time.setter
    def settle_time(self, value):
        self._settle_time = max(float(value), 0) if value is not None or value !='' else None
        self._config['telescope']['settle_time'] = str(self._settle_time) if self._settle_time is not None else ''

    @property
    def autofocus(self):
        return self._autofocus
    
    @property
    def autofocus_driver(self):
        return self._autofocus_driver
    
    @property
    def wcs_driver(self):
        return self._wcs_driver

    @property
    def last_camera_shutter_status(self):
        return self._last_camera_shutter_status
    
    @property
    def current_focus_offset(self):
        return self._current_focus_offset
    
    @property
    def maxim(self):
        return self._maxim

class ObservatoryException(Exception):
    pass