from astropy import coordinates as coord
import configparser
import importlib
import logging
import os
import sys

import drivers.ascom.AscomDriver as AscomDriver
import drivers.abstract_hardware as abs_hd
import drivers.abstract_software as abs_sw

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
        self._config['camera'] = {}; self._config['telescope'] = {}
        self._config['cover_calibrator'] = {}; self._config['dome'] = {}
        self._config['filter_wheel'] = {}; self._config['focuser'] = {}
        self._config['observatory_conditions'] = {}

        self.site_name = 'pyScope Site'
        self.instrument_name = 'pyScope Instrument' 
        self.instrument_description = 'pyScope is a pure-Python telescope control package.'
        self.get_site_from_telescope = False
        self.latitude = None; self.longitude = None; self.elevation = None
        self.diameter = None; self.focal_length = None

        self._camera = None
        self.cooler_setpoint = None; self.cooler_tolerance = None; self.max_dimension = None
        self.pixel_x_size = None; self.pixel_y_size = None
        self.exposure_timeout = 30; self.cooler_timeout = 600

        self._telescope = None
        self.min_altitude = 10; self.telescope_timeout = 600

        self._cover_calibrator = None
        self.cover_calibrator_alt = None; self.cover_calibrator_az = None
        self.cover_calibrator_timeout = 60

        self._dome = None
        self.wait_for_dome_rotation = False; self.dome_timeout = 600

        self._filter_wheel = None
        self.filters = None; self.filter_focus_offsets = None; self.autofocus_filters = None
        self.recentering_filters = None; self.wcs_filters = None; self.filter_wheel_timeout = 60

        self._focuser = None
        self.focuser_max_error = 10; self.focuser_timeout = 60

        self._observatory_conditions = None
        self.observing_conditions_timeout = 60

        self._autofocus = None
        self.autofocus_exposure = 10; self.autofocus_start_position = None; self.autofocus_step_number = 5;
        self.autofocus_step_size = 500; self.autofocus_use_current_pointing = True; self.autofocus_timeout = 600

        self.calibration_filter_exposure = None; self.calibration_filter_focus = None

        self.recenter_exposure = 10; self.recenter_sync_mount = False; self.recenter_timeout = 180

        self._wcs = None

        if config_file_path is not None:
            logging.info('Using config file to initialize observatory: %s' % config_file)
            try: self._config.read(config_file_path)
            except: raise ObservatoryException("Error parsing config file '%s'" % config_file_path)

            # Camera
            self._camera_driver = self.config['camera']['camera_driver']
            self._camera_ascom = self.config['camera']['camera_ascom']
            self._camera = self._import_driver(self.config['camera']['camera_driver'], 'Camera', ascom=self.camera_ascom, required=True)

            # Telescope
            self._telescope_driver = self.config['telescope']['telescope_driver']
            self._telescope_ascom = self.config['telescope']['telescope_ascom']
            self._telescope = self._import_driver(self.telescope_driver, 'Telescope', ascom=self.telescope_ascom, required=True)

            # Cover calibrator
            self._cover_calibrator_driver = self.config.get('cover_calibrator_driver', None)
            self._cover_calibrator_ascom = self.config.get('cover_calibrator_ascom', None)
            self._cover_calibrator = self._import_driver(self.cover_calibrator_driver, 'CoverCalibrator', ascom=self.cover_calibrator_ascom, required=False)

            # Dome
            self._dome_driver = self.config.get('dome_driver', None)
            self._dome_ascom = self.config.get('dome_ascom', None)
            self._dome = self._import_driver(self.dome_driver, 'Dome', ascom=self.dome_ascom, required=False)

            # Filter wheel
            self._filter_wheel_driver = self.config.get('filter_wheel_driver', None)
            self._filter_wheel_ascom = self.config.get('filter_wheel_ascom', None)
            self._filter_wheel = self._import_driver(self.filter_wheel_driver, 'FilterWheel', ascom=self.filter_wheel_ascom, required=False)

            # Focuser
            self._focuser_driver = self.config.get('focuser_driver', None)
            self._focuser_ascom = self.config.get('focuser_ascom', None)
            self._focuser = self._import_driver(self.focuser_driver, 'Focuser', ascom=self.focuser_ascom, required=False)

            # Observing conditions
            self._observing_conditions_driver = self.config.get('observing_conditions_driver', None)
            self._observing_conditions_ascom = self.config.get('observing_conditions_ascom', None)
            self._observing_conditions = self._import_driver(self.observing_conditions_driver, 'ObservingConditions',
                ascom=self.observing_conditions_ascom, required=False)

            # Autofocus
            self._autofocus_driver = self.config.get('autofocus_driver', None)
            self._autofocus_ascom = self.config.get('autofocus_ascom', None)
            self._autofocus = self._import_driver(self.autofocus_driver, 'Autofocus', ascom=self.autofocus_ascom, required=False)

            # WCS
            self._wcs_driver = self.config['recenter'].get('wcs_driver', None)
            self._wcs = self._import_driver(self.wcs_driver, 'WCS', ascom=self.wcs_ascom, required=False)

            # Get other keywords from config file
            master_dict = {**self._config['site'], **self._config['camera'], **self._config['telescope'], **self._config['cover_calibrator'],
                **self._config['dome'], **self._config['filter_wheel'], **self._config['focuser'],
                **self._config['observing_conditions'], **self._config['autofocus'], **self._config['calibration'],
                **self._config['recenter'], **self._config['wcs']}
            self._read_out_kwargs(master_dict)

        # Camera
        self._camera = kwargs.get('camera', self._camera)
        _check_class_inheritance(self._camera, 'Camera')
        self._camera_driver = self._camera.Name
        self._camera_ascom = (AscomDriver in type(self._camera).__bases__)
        self._config['camera']['camera_driver'] = self._camera_driver
        self._config['camera']['camera_ascom'] = str(self._camera_ascom)

        # Telescope
        self._telescope = kwargs.get('telescope', self._telescope)
        _check_class_inheritance(self._telescope, 'Telescope')
        self._telescope_driver = self._telescope.Name
        self._telescope_ascom = (AscomDriver in type(self._telescope).__bases__)
        self._config['telescope']['telescope_driver'] = self._telescope_driver
        self._config['telescope']['telescope_ascom'] = str(self._telescope_ascom)

        # Cover calibrator
        self._cover_calibrator = kwargs.get('cover_calibrator', self._cover_calibrator)
        if self._cover_calibrator is None: self._cover_calibrator = _CoverCalibrator(self)
        _check_class_inheritance(self._cover_calibrator, 'CoverCalibrator')
        self._cover_calibrator_driver = self._cover_calibrator.Name if self._cover_calibrator is not None else ''
        self._cover_calibrator_ascom = (AscomDriver in type(self._cover_calibrator).__bases__) if self._cover_calibrator is not None else False
        self._config['cover_calibrator']['cover_calibrator_driver'] = self._cover_calibrator_driver
        self._config['cover_calibrator']['cover_calibrator_ascom'] = self._cover_calibrator_ascom

        # Dome
        self._dome = kwargs.get('dome', self._dome)
        if self._dome is not None: _check_class_inheritance(self._dome, 'Dome')
        self._dome_driver = self._dome.Name if self._dome is not None else ''
        self._dome_ascom = (AscomDriver in type(self._dome).__bases__) if self._dome is not None else False
        self._config['dome']['dome_driver'] = str(self._dome_driver)
        self._config['dome']['dome_ascom'] = str(self._dome_ascom)

        # Filter wheel
        self._filter_wheel = kwargs.get('filter_wheel', self._filter_wheel)
        if self._filter_wheel is not None: _check_class_inheritance(self._filter_wheel, 'FilterWheel')
        self._filter_wheel_driver = self._filter_wheel.Name if self._filter_wheel is not None else ''
        self._filter_wheel_ascom = (AscomDriver in type(self._filter_wheel).__bases__) if self._filter_wheel is not None else False
        self._config['filter_wheel']['filter_wheel_driver'] = self._filter_wheel_driver
        self._config['filter_wheel']['filter_wheel_ascom'] = self._filter_wheel_ascom

        # Focuser
        self._focuser = kwargs.get('focuser', self._focuser)
        if self._focuser is not None: _check_class_inheritance(self._focuser, 'Focuser')
        self._focuser_driver = self._focuser.Name if self._focuser is not None else ''
        self._focuser_ascom = (AscomDriver in type(self._focuser).__bases__) if self._focuser is not None else 'False'
        self._config['focuser']['focuser_driver'] = self._focuser_driver
        self._config['focuser']['focuser_ascom'] = self._focuser_ascom

        # Observing conditions
        self._observing_conditions = kwargs.get('observing_conditions', self._observing_conditions)
        if self._observing_conditions is not None: _check_class_inheritance(self._observing_conditions, 'ObservingConditions')
        self._observing_conditions_driver = self._observing_conditions.Name if self._observing_conditions is not None else ''
        self._observing_conditions_ascom = (AscomDriver in type(self._observing_conditions).__bases__) if self._observing_conditions is not None else False
        self._config['observing_conditions']['observing_conditions_driver'] = self._observing_conditions_driver
        self._config['observing_conditions']['observing_conditions_ascom'] = self._observing_conditions_ascom

        # Autofocus
        self._autofocus = kwargs.get('autofocus', self._autofocus)
        if self._autofocus is None: self._autofocus = _Autofocus(self)
        _check_class_inheritance(self._autofocus, 'Autofocus')
        self._autofocus_driver = self._autofocus.Name
        self._config['autofocus']['autofocus_driver'] = self._autofocus_driver

        # WCS
        self._wcs = kwargs.get('wcs', self._wcs)
        if self._wcs is None: self._wcs = self._import_driver('wcs_astrometrynet', 'WCS', ascom=False, required=True)
        _check_class_inheritance(self._wcs, 'WCS')
        self._wcs_driver = self._wcs.Name
        self._config['wcs']['wcs_driver'] = self._wcs_driver

        # Get other keywords
        self._read_out_kwargs(kwargs)

    def earth_location(self):
        '''Returns the EarthLocation object for the observatory'''
        return coord.EarthLocation(lat=self.latitude, lon=self.longitude, height=self.elevation)

    def plate_scale(self):
        '''Returns the plate scale of the telescope'''
        return 
    
    def pixel_scale(self):
        '''Returns the pixel scale of the camera'''
        return
        
    def current_lst(self):
        '''Returns the current local sidereal time'''
        return
        
    def sun_altaz(self):
        '''Returns the current altitude of the sun'''
        return 
    
    def moon_altaz(self):
        '''Returns the current altitude of the moon'''
        return
    
    def radec_altaz(self, ra, dec):
        '''Returns the current altitude of an object'''
        return

    def save_config(self, filename=None):
        with open(filename, 'w') as configfile:
            self.config.write(configfile)
    
    def _import_driver(self, driver_name, device, ascom=False, required=False):
        '''Imports a driver'''
        if driver_name is None or driver_name == '':
            if required: raise ObservatoryException("Driver name is required")
            else: return None
        if ascom:
            device = importlib.import_module('drivers.ascom.%s' % device)
            return device(driver_name)
        else:
            try: 
                device_object = importlib.import_module('drivers.%s.%s' % (driver_name, device))
            except:
                try: 
                    driver_path, driver_module = os.path.split(driver_name)
                    driver_module = driver_module.split('.')[0]
                    spec = importlib.util.spec_from_file_location(driver_module, driver_path)
                    device_module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = device_module
                    spec.loader.exec_module(device_module)
                    device_object = getattr(device_module, device)
                except: 
                    if required: raise ObservatoryException("Error importing driver '%s'" % driver_name)
                    else: return None

        return device_object()

    def _check_class_inheritance(self, obj, device):
        if (not getattr(abs_hd, device) in type(obj).__bases__ and 
        not getattr(abs_sw, device) in type(obj).__bases__):
            raise ObservatoryException('Driver %s.%s does not inherit from the required inheritence classes' % (driver_name, device))
    
    def _read_out_kwargs(self, dictionary):
        self.site_name = dictionary.get('site_name', self.site_name)
        self.instrument_name = dictionary.get('instrument_name', self.instrument_name)
        self.instrument_description = dictionary.get('instrument_description', self.instrument_description)
        self.get_site_from_telescope = dictionary.get('get_site_from_telescope', self.get_site_from_telescope)
        self.latitude = dictionary.get('latitude', self.latitude)
        self.longitude = dictionary.get('longitude', self.longitude)
        self.elevation = dictionary.get('elevation', self.elevation)
        self.diameter = dictionary.get('diameter', self.diameter)
        self.focal_length = dictionary.get('focal_length', self.focal_length)

        self.cooler_setpoint = dictionary.get('cooler_setpoint', self.cooler_setpoint)
        self.cooler_tolerance = dictionary.get('cooler_tolerance', self.cooler_tolerance)
        self.max_dimension = dictionary.get('max_dimension', self.max_dimension)
        self.pixel_x_size = dictionary.get('pixel_x_size', self.pixel_x_size)
        self.pixel_y_size = dictionary.get('pixel_y_size', self.pixel_y_size)
        self.exposure_timeout = dictionary.get('exposure_timeout', self.exposure_timeout)
        self.cooler_timeout = dictionary.get('cooler_timeout', self.cooler_timeout)

        self.min_altitude = dictionary.get('min_altitude', self.min_altitude)
        self.telescope_timeout = dictionary.get('telescope_timeout', self.telescope_timeout)

        self.cover_calibrator_alt = dictionary.get('cover_calibrator_alt', self.cover_calibrator_alt)
        self.cover_calibrator_az = dictionary.get('cover_calibrator_az', self.cover_calibrator_az)
        self.cover_calibrator_timeout = dictionary.get('cover_calibrator_timeout', self.cover_calibrator_timeout)

        self.wait_for_dome_rotation = dictionary.get('wait_for_dome_rotation', self.wait_for_dome_rotation)
        self.dome_timeout = dictionary.get('dome_timeout', self.dome_timeout)

        self.filters = dictionary.get('filters', self.filters)
        self.filter_focus_offsets = dictionary.get('filter_focus_offsets', self.filter_focus_offsets)
        self.autofocus_filters = dictionary.get('autofocus_filters', self.autofocus_filters)
        self.recentering_filters = dictionary.get('recentering_filters', self.recentering_filters)
        self.wcs_filters = dictionary.get('wcs_filters', self.wcs_filters)
        self.filter_wheel_timeout = dictionary.get('filter_wheel_timeout', self.filter_wheel_timeout)

        self.focuser_max_error = dictionary.get('focuser_max_error', self.focuser_max_error)
        self.focuser_timeout = dictionary.get('focuser_timeout', self.focuser_timeout)

        self.observatory_conditions_timeout = dictionary.get('observatory_conditions_timeout', self.observatory_conditions_timeout)

        self.autofocus_exposure = dictionary.get('autofocus_exposure', self.autofocus_exposure)
        self.autofocus_start_position = dictionary.get('autofocus_start_position', self.autofocus_start_position)
        self.autofocus_step_number = dictionary.get('autofocus_step_number', self.autofocus_step_number)
        self.autofocus_step_size = dictionary.get('autofocus_step_size', self.autofocus_step_size)
        self.autofocus_use_current_pointing = dictionary.get('autofocus_use_current_pointing', self.autofocus_use_current_pointing)
        self.autofocus_timeout = dictionary.get('autofocus_timeout', self.autofocus_timeout)

        self.calibration_filter_exposure = dictionary.get('calibration_filter_exposure', self.calibration_filter_exposure)
        self.calibration_filter_timeout = dictionary.get('calibration_filter_timeout', self.calibration_filter_timeout)

        self.recenter_exposure = dictionary.get('recentering_exposure', self.recenter_exposure)
        self.recenter_sync_mount = dictionary.get('recentering_sync_mount', self.recenter_sync_mount)
        self.recenter_timeout = dictionary.get('recentering_timeout', self.recenter_timeout)

        self.ra_key = dictionary.get('ra_key', self.ra_key)
        self.dec_key = dictionary.get('dec_key', self.dec_key)
        self.wcs_timeout = dictionary.get('wcs_timeout', self.wcs_timeout)

    @property
    def config(self):
        return self._config

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
    def diameter(self):
        return self._diameter
    @diameter.setter
    def diameter(self, value):
        self._diameter = max(float(value), 0) if value is not None or value !='' else None
        self._config['site']['diameter'] = str(self._diameter) if self._diameter is not None else ''
    
    @property
    def focal_length(self):
        return self._focal_length
    @focal_length.setter
    def focal_length(self, value):
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
    def pixel_x_size(self):
        return self._pixel_x_size
    @pixel_x_size.setter
    def pixel_x_size(self, value):
        self._pixel_x_size = max(float(value), 0) if value is not None or value !='' else None
        self._config['camera']['pixel_x_size'] = str(self._pixel_x_size) if self._pixel_x_size is not None else ''

    @property
    def pixel_y_size(self):
        return self._pixel_y_size
    @pixel_y_size.setter
    def pixel_y_size(self, value):
        self._pixel_y_size = max(float(value), 0) if value is not None or value !='' else None
        self._config['camera']['pixel_y_size'] = str(self._pixel_y_size) if self._pixel_y_size is not None else ''
    
    @property
    def exposure_timeout(self):
        return self._exposure_timeout
    @exposure_timeout.setter
    def exposure_timeout(self, value):
        self._exposure_timeout = max(float(value), 0) if value is not None or value !='' else None
        self._config['camera']['exposure_timeout'] = str(self._exposure_timeout) if self._exposure_timeout is not None else ''
    
    @property
    def cooler_timeout(self):
        return self._cooler_timeout
    @cooler_timeout.setter
    def cooler_timeout(self, value):
        self._cooler_timeout = max(float(value), 0) if value is not None or value !='' else None
        self._config['camera']['cooler_timeout'] = str(self._cooler_timeout) if self._cooler_timeout is not None else ''

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
    def cover_calibrator_timeout(self):
        return self._cover_calibrator_timeout
    @cover_calibrator_timeout.setter
    def cover_calibrator_timeout(self, value):
        self._cover_calibrator_timeout = max(float(value), 0) if value is not None or value !='' else None
        self._config['cover_calibrator']['cover_calibrator_timeout'] = str(self._cover_calibrator_timeout) if self._cover_calibrator_timeout is not None else ''

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
    def wait_for_dome_rotation(self):
        return self._wait_for_dome_rotation
    @wait_for_dome_rotation.setter
    def wait_for_dome_rotation(self, value):
        self._wait_for_dome_rotation = bool(value)
        self._config['dome']['wait_for_dome_rotation'] = str(self._wait_for_dome_rotation)
    
    @property
    def dome_timeout(self):
        return self._dome_timeout
    @dome_timeout.setter
    def dome_timeout(self, value):
        self._dome_timeout = max(float(value), 0) if value is not None or value !='' else None
        self._config['dome']['dome_timeout'] = str(self._dome_timeout) if self._dome_timeout is not None else ''

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
    def autofocus_filters(self):
        return self._autofocus_filters
    @autofocus_filters.setter
    def autofocus_filters(self, *args):
        if args is None or value == '': self._autofocus_filters = None
        for value in args:
            if char(value) in self.filters: self._autofocus_filters.append(char(value))
            else: raise ObservatoryException('Filter %s is not in the list of filters' % value)
        self._config['filter_wheel']['autofocus_filters'] = ', '.join(self._autofocus_filters) if self._autofocus_filters is not None else ''
    @autofocus_filters.deleter
    def autofocus_filters(self, *args):
        for value in args:
            self._autofocus_filters.remove(char(value))
        self._config['filter_wheel']['autofocus_filters'] = ', '.join(self._autofocus_filters)
    
    @property
    def recentering_filters(self):
        return self._recentering_filters
    @recentering_filters.setter
    def recentering_filters(self, *args):
        if args is None or value == '': self._recentering_filters = None
        for value in args:
            if char(value) in self.filters: self._recentering_filters.append(char(value))
            else: raise ObservatoryException('Filter %s is not in the list of filters' % value)
        self._config['filter_wheel']['recentering_filters'] = ', '.join(self._recentering_filters) if self._recentering_filters is not None else ''
    @recentering_filters.deleter
    def recentering_filters(self, *args):
        for value in args:
            self._recentering_filters.remove(char(value))
        self._config['filter_wheel']['recentering_filters'] = ', '.join(self._recentering_filters)
    
    @property
    def wcs_filters(self):
        return self._wcs_filters
    @wcs_filters.setter
    def wcs_filters(self, *args):
        if args is None or value == '': self._wcs_filters = None
        for value in args:
            if char(value) in self.filters: self._wcs_filters.append(char(value))
            else: raise ObservatoryException('Filter %s is not in the list of filters' % value)
        self._config['filter_wheel']['wcs_filters'] = ', '.join(self._wcs_filters) if self._wcs_filters is not None else ''
    @wcs_filters.deleter
    def wcs_filters(self, *args):
        for value in args:
            self._wcs_filters.remove(char(value))
        self._config['filter_wheel']['wcs_filters'] = ', '.join(self._wcs_filters)
    
    @property
    def filter_wheel_timeout(self):
        return self._filter_wheel_timeout
    @filter_wheel_timeout.setter
    def filter_wheel_timeout(self, value):
        self._filter_wheel_timeout = max(float(value), 0) if value is not None or value !='' else None
        self._config['filter_wheel']['filter_wheel_timeout'] = str(self._filter_wheel_timeout) if self._filter_wheel_timeout is not None else ''
    
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
    def focuser_timeout(self):
        return self._focuser_timeout
    @focuser_timeout.setter
    def focuser_timeout(self, value):
        self._focuser_timeout = max(float(value), 0) if value is not None or value !='' else None
        self._config['focuser']['focuser_timeout'] = str(self._focuser_timeout) if self._focuser_timeout is not None else ''

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
    def observing_conditions_timeout(self):
        return self._observing_conditions_timeout
    @observing_conditions_timeout.setter
    def observing_conditions_timeout(self, value):
        self._observing_conditions_timeout = max(float(value), 0) if value is not None or value !='' else None
        self._config['observing_conditions']['observing_conditions_timeout'] = str(self._observing_conditions_timeout) if self._observing_conditions_timeout is not None else ''
    
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
    def telescope_timeout(self):
        return self._telescope_timeout
    @telescope_timeout.setter
    def telescope_timeout(self, value):
        self._telescope_timeout = max(float(value), 0) if value is not None or value !='' else None
        self._config['telescope']['telescope_timeout'] = str(self._telescope_timeout) if self._telescope_timeout is not None else ''

    @property
    def autofocus(self):
        return self._autofocus
    
    @property
    def autofocus_driver(self):
        return self._autofocus_driver
    
    @property
    def autofocus_exposure(self):
        return self._autofocus_exposure
    @autofocus_exposure.setter
    def autofocus_exposure(self, value):
        self._autofocus_exposure = max(float(value), 0) if value is not None or value !='' else None
        self._config['autofocus']['autofocus_exposure'] = str(self._autofocus_exposure) if self._autofocus_exposure is not None else ''
    
    @property
    def autofocus_start_position(self):
        return self._autofocus_start_position
    @autofocus_start_position.setter
    def autofocus_start_position(self, value):
        self._autofocus_start_position = max(float(value), 0) if value is not None or value !='' else None
        self._config['autofocus']['autofocus_start_position'] = str(self._autofocus_start_position) if self._autofocus_start_position is not None else ''
    
    @property
    def autofocus_step_number(self):
        return self._autofocus_step_number
    @autofocus_step_number.setter
    def autofocus_step_number(self, value):
        self._autofocus_step_number = max(int(value), 0) if value is not None or value !='' else None
        self._config['autofocus']['autofocus_step_number'] = str(self._autofocus_step_number) if self._autofocus_step_number is not None else ''
    
    @property
    def autofocus_step_size(self):
        return self._autofocus_step_size
    @autofocus_step_size.setter
    def autofocus_step_size(self, value):
        self._autofocus_step_size = max(float(value), 0) if value is not None or value !='' else None
        self._config['autofocus']['autofocus_step_size'] = str(self._autofocus_step_size) if self._autofocus_step_size is not None else ''
    
    @property
    def autofocus_use_current_pointing(self):
        return self._autofocus_use_current_pointing
    @autofocus_use_current_pointing.setter
    def autofocus_use_current_pointing(self, value):
        self._autofocus_use_current_pointing = bool(value)
        self._config['autofocus']['autofocus_use_current_pointing'] = str(self._autofocus_use_current_pointing)
    
    @property
    def autofocus_timeout(self):
        return self._autofocus_timeout
    @autofocus_timeout.setter
    def autofocus_timeout(self, value):
        self._autofocus_timeout = max(float(value), 0) if value is not None or value !='' else None
        self._config['autofocus']['autofocus_timeout'] = str(self._autofocus_timeout) if self._autofocus_timeout is not None else ''
    
    @property
    def calibration_filter_exposure_time(self):
        return self._calibration_filter_exposure_time
    @calibration_filter_exposure_time.setter
    def calibration_filter_exposure_time(self, value, filt=None):
        if filt is None: self._calibration_filter_exposure_time = dict(zip(self.filters, value)) if value is not None or value !='' else None
        else: self._calibration_filter_exposure_time[filt] = float(value) if value is not None or value !='' else None
        self._config['calibration']['calibration_filter_exposure_time'] = ', '.join(self._calibration_filter_exposure_time.values()) if self._calibration_filter_exposure_time is not None else ''
    
    @property
    def calibration_filter_brightness(self):
        return self._calibration_filter_brightness
    @calibration_filter_brightness.setter
    def calibration_filter_brightness(self, value):
        if filt is None: self._calibration_filter_brightness = dict(zip(self.filters, value)) if value is not None or value !='' else None
        else: self._calibration_filter_brightness[filt] = float(value) if value is not None or value !='' else None
        self._config['calibration']['calibration_filter_brightness'] = ', '.join(self._calibration_filter_brightness.values()) if self._calibration_filter_brightness is not None else ''
    
    @property
    def recenter_exposure(self):
        return self._recenter_exposure
    @recenter_exposure.setter
    def recenter_exposure(self, value):
        self._recenter_exposure = max(float(value), 0) if value is not None or value !='' else None
        self._config['recenter']['recenter_exposure'] = str(self._recenter_exposure) if self._recenter_exposure is not None else ''
    
    @property
    def recenter_sync_mount(self):
        return self._recenter_sync_mount
    @sync_mount.setter
    def recenter_sync_mount(self, value):
        self._recenter_sync_mount = bool(value)
        self._config['recenter']['recenter_sync_mount'] = str(self._recenter_sync_mount)
    
    @property
    def recenter_timeout(self):
        return self._recenter_timeout
    @recenter_timeout.setter
    def recenter_timeout(self, value):
        self._recenter_timeout = max(float(value), 0) if value is not None or value !='' else None
        self._config['recenter']['recenter_timeout'] = str(self._recenter_timeout) if self._recenter_timeout is not None else ''
    
    @property
    def wcs_driver(self):
        return self._wcs_driver
    
    @property
    def ra_key(self):
        return self._ra_key
    @ra_key.setter
    def ra_key(self, value):
        self._ra_key = str(value) if value is not None or value !='' else None
        self._config['wcs']['ra_key'] = str(self._ra_key) if self._ra_key is not None else ''

    @property
    def dec_key(self):
        return self._dec_key
    @dec_key.setter
    def dec_key(self, value):
        self._dec_key = str(value) if value is not None or value !='' else None
        self._config['wcs']['dec_key'] = str(self._dec_key) if self._dec_key is not None else ''

    @property
    def wcs_timeout(self):
        return self._wcs_timeout
    @wcs_timeout.setter
    def wcs_timeout(self, value):
        self._wcs_timeout = max(float(value), 0) if value is not None or value !='' else None
        self._config['wcs']['wcs_timeout'] = str(self._wcs_timeout) if self._wcs_timeout is not None else ''

class _Autofocus(abs_sw.Autofocus):
    def __init__(self, Observatory):
        pass

class _CoverCalibrator(abs_hw.CoverCalibrator):
    def __init__(self, Observatory):
        pass

class ObservatoryException(Exception):
    pass