from astropy import coordinates as coord, time as astrotime
import astropy.wcs, astropy.io.fits as pyfits
from astroquery.mpc import MPC
import numpy as np
import configparser
import logging
import tempfile
import time
import shutil

from pyscope import Autofocus, Camera, CoverCalibrator, Dome, FilterWheel, Focuser, ObservingConditions
from pyscope import Rotator, SafetyMonitor, Switch, Telescope, WCS

from pyscope._driver_utils import _check_class_inheritance
from pyscope.drivers._ascom import Driver as AscomDriver
from . import __version__

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

        self.site_name = 'pyScope Site'
        self.instrument_name = 'pyScope Instrument' 
        self.instrument_description = 'pyScope is a pure-Python telescope control package.'
        self.get_site_from_telescope = True
        self.latitude = None; self.longitude = None; self.elevation = None
        self.get_optics_from_telescope = True
        self.diameter = None; self.focal_length = None

        self._camera = None
        self.cooler_setpoint = None; self.cooler_tolerance = None; self.max_dimension = None
        self.default_readout_mode = None

        self._cover_calibrator = None
        self.cover_calibrator_alt = None; self.cover_calibrator_az = None

        self._dome = None

        self._filter_wheel = None
        self.filters = None; self.filter_focus_offsets = None

        self._focuser = None
        self.focuser_max_error = 10

        self._observing_conditions = None

        self._rotator = None
        self.rotator_reverse = False; self.rotator_min_angle = None; self.rotator_max_angle = None

        self._safety_monitor = None

        self._switch = None

        self._telescope = None
        self.min_altitude = 10

        self._autofocus = None
        self.autofocus_exposure = 10; self.autofocus_start_position = None; self.autofocus_step_number = 5;
        self.autofocus_step_size = 500; self.autofocus_use_current_pointing = True

        if config_file_path is not None:
            logging.info('Using config file to initialize observatory: %s' % config_file)
            try: self._config.read(config_file_path)
            except: raise ObservatoryException("Error parsing config file '%s'" % config_file_path)

            # Camera
            self._camera_driver = self.config['camera']['camera_driver']
            self._camera_ascom = self.config['camera']['camera_ascom']
            self._camera = Camera(self.camera_driver, ascom=self.camera_ascom)

            # Cover calibrator
            self._cover_calibrator_driver = self.config.get('cover_calibrator', 'cover_calibrator_driver', fallback=None)
            self._cover_calibrator_ascom = self.config.get('cover_calibrator', 'cover_calibrator_ascom', fallback=None)
            self._cover_calibrator = CoverCalibrator(self.cover_calibrator_driver, ascom=self.cover_calibrator_ascom)

            # Dome
            self._dome_driver = self.config.get('dome', 'dome_driver', fallback=None)
            self._dome_ascom = self.config.get('dome', 'dome_ascom', fallback=None)
            self._dome = Dome(self.dome_driver, ascom=self.dome_ascom)

            # Filter wheel
            self._filter_wheel_driver = self.config.get('filter_wheel', 'filter_wheel_driver', fallback=None)
            self._filter_wheel_ascom = self.config.get('filter_wheel', 'filter_wheel_ascom', fallback=None)
            self._filter_wheel = FilterWheel(self.filter_wheel_driver, ascom=self.filter_wheel_ascom)

            # Focuser
            self._focuser_driver = self.config.get('focuser', 'focuser_driver', fallback=None)
            self._focuser_ascom = self.config.get('focuser', 'focuser_ascom', fallback=None)
            self._focuser = Focuser(self.focuser_driver, ascom=self.focuser_ascom)

            # Observing conditions
            self._observing_conditions_driver = self.config.get('observing_conditions', 'observing_conditions_driver', fallback=None)
            self._observing_conditions_ascom = self.config.get('observing_conditions', 'observing_conditions_ascom', fallback=None)
            self._observing_conditions = ObservingConditions(self.observing_conditions_driver, ascom=self.observing_conditions_ascom)

            # Rotator
            self._rotator_driver = self.config.get('rotator', 'rotator_driver', fallback=None)
            self._rotator_ascom = self.config.get('rotator', 'rotator_ascom', fallback=None)
            self._rotator = Rotator(self.rotator_driver, ascom=self.rotator_ascom)

            # Safety monitor
            for val in self.config['safety_monitor'].values():
                try: 
                    driver, ascom = val.replace(' ', '').split(',')
                    self._safety_monitor_driver.append(driver)
                    self._safety_monitor_ascom.append(ascom)
                    self._safety_monitor.append(SafetyMonitor(driver, ascom=ascom))
                except:
                    pass

            # Switch
            for val in self.config['switch'].values():
                try: 
                    driver, ascom = val.replace(' ', '').split(',')
                    self._switch_driver.append(driver)
                    self._switch_ascom.append(ascom)
                    self._switch.append(Switch(driver, ascom=ascom))
                except:
                    pass

            # Telescope
            self._telescope_driver = self.config['telescope']['telescope_driver']
            self._telescope_ascom = self.config['telescope']['telescope_ascom']
            self._telescope = Telescope(self.telescope_driver, ascom=self.telescope_ascom)

            # Autofocus
            self._autofocus_driver = self.config.get('autofocus', 'autofocus_driver', fallback=None)
            self._autofocus_ascom = self.config.get('autofocus', 'autofocus_ascom', fallback=None)
            self._autofocus = Autofocus(self.autofocus_driver, ascom=self.autofocus_ascom)

            # WCS
            self._wcs_driver = self.config.get('wcs', 'wcs_driver', fallback=None)
            self._wcs = WCS(self.wcs_driver)

            # Get other keywords from config file
            master_dict = {**self._config['site'], **self._config['camera'], **self._config['cover_calibrator'],
                **self._config['dome'], **self._config['filter_wheel'], **self._config['focuser'],
                **self._config['observing_conditions'], **self._config['rotator'], **self._config['safety_monitor'],
                **self._config['switch'], **self._config['telescope'], **self._config['autofocus'], 
                **self._config['wcs']}
            self._read_out_kwargs(master_dict)

        # Camera
        self._camera = kwargs.get('camera', self._camera)
        _check_class_inheritance(type(self._camera), 'Camera')
        self._camera_driver = self._camera.Name
        self._camera_ascom = (AscomDriver in type(self._camera).__bases__)
        self._config['camera']['camera_driver'] = self._camera_driver
        self._config['camera']['camera_ascom'] = str(self._camera_ascom)

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

        # Rotator
        self._rotator = kwargs.get('rotator', self._rotator)
        if self._rotator is not None: _check_class_inheritance(self._rotator, 'Rotator')
        self._rotator_driver = self._rotator.Name if self._rotator is not None else ''
        self._rotator_ascom = (AscomDriver in type(self._rotator).__bases__) if self._rotator is not None else False
        self._config['rotator']['rotator_driver'] = self._rotator_driver
        self._config['rotator']['rotator_ascom'] = self._rotator_ascom

        # Safety monitor
        kwarg = kwargs.get('safety_monitor', self._safety_monitor)
        if type(kwarg) is not list: 
            self._safety_monitor = kwarg
            self._safety_monitor_driver = self._safety_monitor.Name if self._safety_monitor is not None else ''
            self._safety_monitor_ascom = (AscomDriver in type(self._safety_monitor).__bases__) if self._safety_monitor is not None else False
            self._config['safety_monitor']['driver_0'] = (self._safety_monitor_driver + ',' + str(self._safety_monitor_ascom)) if self._safety_monitor_driver != '' else ''
        else: 
            self._safety_monitor = kwarg
            self._safety_monitor_driver = [None] * len(self._safety_monitor)
            self._safety_monitor_ascom = [None] * len(self._safety_monitor)
            for i, safety_monitor in enumerate(self._safety_monitor):
                if safety_monitor is not None: _check_class_inheritance(safety_monitor, 'SafetyMonitor')
                self._safety_monitor_driver[i] = safety_monitor.Name if safety_monitor is not None else ''
                self._safety_monitor_ascom[i] = (AscomDriver in type(safety_monitor).__bases__) if safety_monitor is not None else False
                self._config['safety_monitor']['driver_%i' % i] = (self._safety_monitor_driver[i] + ',' + str(self._safety_monitor_ascom[i])) if self._safety_monitor_driver[i] != '' else ''

        # Switch
        kwarg = kwargs.get('switch', self._switch)
        if type(kwarg) is not list or type(kwarg) is not tuple: 
            self._switch = kwarg
            self._switch_driver = self._switch.Name if self._switch is not None else ''
            self._switch_ascom = (AscomDriver in type(self._switch).__bases__) if self._switch is not None else False
            self._config['switch']['driver_0'] = (self._switch_driver + ',' + str(self._switch_ascom)) if self._switch_driver != '' else ''
        else: 
            self._switch = kwarg
            self._switch_driver = [None] * len(self._switch)
            self._switch_ascom = [None] * len(self._switch)
            for i, switch in enumerate(self._switch):
                if switch is not None: _check_class_inheritance(switch, 'Switch')
                self._switch_driver[i] = switch.Name if switch is not None else ''
                self._switch_ascom[i] = (AscomDriver in type(switch).__bases__) if switch is not None else False
                self._config['switch']['driver_%i' % i] = (self._switch_driver[i] + ',' + str(self._switch_ascom[i])) if self._switch_driver[i] != '' else ''

        # Telescope
        self._telescope = kwargs.get('telescope', self._telescope)
        _check_class_inheritance(self._telescope, 'Telescope')
        self._telescope_driver = self._telescope.Name
        self._telescope_ascom = (AscomDriver in type(self._telescope).__bases__)
        self._config['telescope']['telescope_driver'] = self._telescope_driver
        self._config['telescope']['telescope_ascom'] = str(self._telescope_ascom)

        # Autofocus
        self._autofocus = kwargs.get('autofocus', self._autofocus)
        if self._autofocus is not None: _check_class_inheritance(self._autofocus, 'Autofocus')
        self._autofocus_driver = self._autofocus.Name
        self._config['autofocus']['autofocus_driver'] = self._autofocus_driver

        # WCS
        self._wcs = kwargs.get('wcs', self._wcs)
        if self._wcs is None: self._wcs = WCS('wcs_astrometrynet')
        _check_class_inheritance(self._wcs, 'WCS')
        self._wcs_driver = self._wcs.Name
        self._config['wcs']['wcs_driver'] = self._wcs_driver

        # Get other keywords
        self._read_out_kwargs(kwargs)

        # Non-keyword properties
        self._last_camera_shutter_status = None
        self.camera.OriginalStartExposure = self.camera.StartExposure
        def NewStartExposure(self, Duration, Light):
            self._last_camera_shutter_status = Light
            self.camera.OriginalStartExposure(Duration, Light)
        self.camera.StartExposure = NewStartExposure
    
    def connect_all(self):
        '''Connects to the observatory'''

        self.camera.Connected = True
        if self.camera.Connected: self.logger.info('Camera connected')
        else: self.logger.warning('Camera failed to connect')

        if self.cover_calibrator is not None:
            self.cover_calibrator.Connected = True
            if self.cover_calibrator.Connected: self.logger.info('Cover calibrator connected')
            else: self.logger.warning('Cover calibrator failed to connect')
        
        if self.dome is not None:
            self.dome.Connected = True
            if self.dome.Connected: self.logger.info('Dome connected')
            else: self.logger.warning('Dome failed to connect')
        
        if self.filter_wheel is not None:
            self.filter_wheel.Connected = True
            if self.filter_wheel.Connected: self.logger.info('Filter wheel connected')
            else: self.logger.warning('Filter wheel failed to connect')
        
        if self.focuser is not None:
            self.focuser.Connected = True
            if self.focuser.Connected: self.logger.info('Focuser connected')
            else: self.logger.warning('Focuser failed to connect')
        
        if self.observing_conditions is not None:
            self.observing_conditions.Connected = True
            if self.observing_conditions.Connected: self.logger.info('Observing conditions connected')
            else: self.logger.warning('Observing conditions failed to connect')
        
        if self.rotator is not None:
            self.rotator.Connected = True
            if self.rotator.Connected: self.logger.info('Rotator connected')
            else: self.logger.warning('Rotator failed to connect')
        
        if self.safety_monitor is not None:
            for safety_monitor in self.safety_monitor:
                safety_monitor.Connected = True
                if safety_monitor.Connected: self.logger.info('Safety monitor %s connected' % safety_monitor.Name)
                else: self.logger.warning('Safety monitor %s failed to connect' % safety_monitor.Name)
            
        if self.switch is not None:
            for switch in self.switch:
                switch.Connected = True
                if switch.Connected: self.logger.info('Switch %s connected' % switch.Name)
                else: self.logger.warning('Switch %s failed to connect' % switch.Name)
        
        self.telescope.Connected = True
        if self.telescope.Connected: self.logger.info('Telescope connected')
        else: self.logger.warning('Telescope failed to connect')

        return True
    
    def disconnect_all(self):
        '''Disconnects from the observatory'''

        self.camera.Connected = False
        if not self.camera.Connected: self.logger.info('Camera disconnected')
        else: self.logger.warning('Camera failed to disconnect')

        if self.cover_calibrator is not None:
            self.cover_calibrator.Connected = False
            if not self.cover_calibrator.Connected: self.logger.info('Cover calibrator disconnected')
            else: self.logger.warning('Cover calibrator failed to disconnect')
        
        if self.dome is not None:
            self.dome.Connected = False
            if not self.dome.Connected: self.logger.info('Dome disconnected')
            else: self.logger.warning('Dome failed to disconnect')
        
        if self.filter_wheel is not None:
            self.filter_wheel.Connected = False
            if not self.filter_wheel.Connected: self.logger.info('Filter wheel disconnected')
            else: self.logger.warning('Filter wheel failed to disconnect')
        
        if self.focuser is not None:
            self.focuser.Connected = False
            if not self.focuser.Connected: self.logger.info('Focuser disconnected')
            else: self.logger.warning('Focuser failed to disconnect')

        if self.observing_conditions is not None:
            self.observing_conditions.Connected = False
            if not self.observing_conditions.Connected: self.logger.info('Observing conditions disconnected')
            else: self.logger.warning('Observing conditions failed to disconnect')
        
        if self.rotator is not None:
            self.rotator.Connected = False
            if not self.rotator.Connected: self.logger.info('Rotator disconnected')
            else: self.logger.warning('Rotator failed to disconnect')
        
        if self.safety_monitor is not None:
            for safety_monitor in self.safety_monitor:
                safety_monitor.Connected = False
                if not safety_monitor.Connected: self.logger.info('Safety monitor %s disconnected' % safety_monitor.Name)
                else: self.logger.warning('Safety monitor %s failed to disconnect' % safety_monitor.Name)
        
        if self.switch is not None:
            for switch in self.switch:
                switch.Connected = False
                if not switch.Connected: self.logger.info('Switch %s disconnected' % switch.Name)
                else: self.logger.warning('Switch %s failed to disconnect' % switch.Name)
            
        self.telescope.Connected = False
        if not self.telescope.Connected: self.logger.info('Telescope disconnected')
        else: self.logger.warning('Telescope failed to disconnect')

        return True
    
    def shutdown(self):
        '''Shuts down the observatory'''

        self.logger.info('Shutting down observatory')

        logging.info('Aborting any in-progress camera exposures...')
        try:
            self.camera.AbortExposure()
        except: logging.exception('Error aborting exposure during shutdown')

        logging.info('Attempting to take a dark exposure to close camera shutter...')
        try:
            self.camera.StartExposure(0, False)
            while self.camera.ImageReady is False:
                time.sleep(0.1)
        except: logging.exception('Error closing camera shutter during shutdown')

        if self.dome is not None:
            logging.info('Aborting any dome motion...')
            try: self.dome.AbortSlew()
            except: logging.exception('Error aborting dome motion during shutdown')

            if self.dome.CanFindPark:
                logging.info('Attempting to park dome...')
                try: self.dome.Park()
                except: logging.exception('Error parking dome during shutdown')

            if self.dome.CanSetShutter:
                logging.info('Attempting to close dome shutter...')
                try: self.dome.CloseShutter()
                except: logging.exception('Error closing dome shutter during shutdown')
        
        if self.focuser is not None:
            logging.info('Aborting any in-progress filter wheel motion...')
            try: self.focuser.Halt()
            except: logging.exception('Error aborting filter wheel motion during shutdown')
        
        if self.rotator is not None:
            logging.info('Aborting any in-progress rotator motion...')
            try: self.rotator.Halt()
            except: logging.exception('Error stopping rotator during shutdown')
        
        logging.info('Aborting any in-progress telescope slews...')
        try: self.telescope.AbortSlew()
        except: logging.exception('Error aborting slew during shutdown')

        logging.info('Attempting to turn off telescope tracking...')
        try: self.telescope.Tracking = False
        except: logging.exception('Error turning off telescope tracking during shutdown')

        if self.telescope.CanPark:
            logging.info('Attempting to park telescope...')
            try: self.telescope.Park()
            except: logging.exception('Error parking telescope during shutdown')
        elif self.telescope.CanFindHome:
            logging.info('Attempting to find home position...')
            try: self.telescope.FindHome()
            except: logging.exception('Error finding home position during shutdown')

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

    def get_object_altaz(self, obj, ra, dec, unit=('hr', 'deg'), frame='icrs', t=None):
        '''Returns the altitude and azimuth of the requested object at the requested time'''
        obj = self._parse_obj_ra_dec(obj, ra, dec, unit, frame)
        if t is None: t = self.observatory_time
        t = Time(t)

        return obj.transform_to(coord.AltAz(obstime=t, location=self.observatory_location))
    
    def get_object_slew(self, obj, ra, dec, unit=('hr', 'deg'), frame='icrs', t=None):
        '''Determines the slew coordinates of the requested object at the requested time'''
        obj = self._parse_obj_ra_dec(obj, ra, dec, unit, frame)
        if t is None: t = self.observatory_time
        t = Time(t)

        eq_system = self.telescope.EquatorialSystem
        if eq_system == 0:
            logging.warning('Telescope equatorial system is not set, assuming Topocentric')
            eq_system = 1
        
        if eq_system == 1: obj_slew = obj.transform_to(coord.TETE(obstime=t, location=self.observatory_location))
        elif eq_system == 2: obj_slew = obj.transform_to('icrs')
        elif eq_system == 3:
            logging.info('Astropy does not support J2050 ICRS yet, using FK5')
            obj_slew = obj.transform_to(coord.FK5(equinox='J2050'))
        elif eq_system == 4: obj_slew = obj.transform_to(coord.FK4(equinox='B1950'))

        return obj_slew
    
    def save_last_image(self, filename, frametyp=None, target=None, do_wcs=False, wcs_kwargs=None, overwrite=False):
        '''Saves the current image'''

        if not self.camera.ImageReady:
            logging.warning('Image is not ready.')
            return False
        
        if (self.camera.ImageArray is None or self.camera.ImageArray.size == 0 
            or self.camera.ImageArray.shape[0] == 0 or self.camera.ImageArray.shape[1] == 0):
            logging.warning('Image array is empty.')
            return False
        
        hdr = pyfits.Header()

        hdr['SIMPLE'] = True
        hdr['BITPIX'] = (16, '8 unsigned int, 16 & 32 int, -32 & -64 real')
        hdr['NAXIS'] = (2, 'number of axes')
        hdr['NAXIS1'] = (self.camera.ImageArray.shape[0], 'fastest changing axis')
        hdr['NAXIS2'] = (self.camera.ImageArray.shape[1], 'next to fastest changing axis')
        if frametyp is not None: hdr['FRAMETYP'] = (frametyp, 'Frame type')
        elif self.last_camera_shutter_status: hdr['FRAMETYP'] = ('Light', 'Frame type') 
        elif not self.last_camera_shutter_status: hdr['FRAMETYP'] = ('Dark', 'Frame type')
        hdr['BSCALE'] = (1, 'physical=BZERO + BSCALE*array_value')
        hdr['BZERO'] = (32768, 'physical=BZERO + BSCALE*array_value')
        hdr['SWCREATE'] = ('pyScope', 'Software used to create file')
        hdr['SWVERSIO'] = (__version__, 'Version of software used to create file')
        hdr['ROWORDER'] = ('TOP-DOWN', 'Row order of image')
        
        hdr['DATE-OBS'] = (self.camera.LastExposureStartTime, 'YYYY-MM-DDThh:mm:ss observation start, UT')
        hdr['JD'] = (astrotime.Time(self.camera.LastExposureStartTime).jd, 'Julian date')
        hdr['MJD'] = (astrotime.Time(self.camera.LastExposureStartTime).mjd, 'Modified Julian date')
        hdr['EXPTIME'] = (self.camera.LastExposureDuration, 'Exposure time in seconds')
        hdr['EXPOSURE'] = (self.camera.LastExposureDuration, 'Exposure time in seconds')
        hdr['SET-TEMP'] = (self.camera.CoolerSetPoint, 'CCD temperature setpoint in C')
        hdr['CCD-TEMP'] = (self.camera.CCDTemperature, 'CCD temperature in C')
        if self.camera.CanGetCoolerPower: hdr['COOLERPOW'] = (self.camera.CoolerPower, 'Cooler power in percent')
        hdr['XPIXSZ'] = (self.camera.PixelSizeX, 'Pixel size in microns')
        hdr['YPIXSZ'] = (self.camera.PixelSizeY, 'Pixel size in microns')
        hdr['XBINNING'] = (self.camera.BinX, 'Binning factor in width')
        hdr['YBINNING'] = (self.camera.BinY, 'Binning factor in height')
        hdr['XORGSUBF'] = (self.camera.StartX, 'Subframe X position')
        hdr['YORGSUBF'] = (self.camera.StartY, 'Subframe Y position')
        hdr['XPOSSUBF'] = (self.camera.NumX, 'Subframe X dimension')
        hdr['YPOSSUBF'] = (self.camera.NumY, 'Subframe Y dimension')
        hdr['READOUT'] = (self.camera.ReadoutMode, 'Readout mode of image')
        hdr['FOCALLEN'] = (self.focal_length, 'Focal length of telescope in mm')
        hdr['APTDIA'] = (self.diameter, 'Aperture diameter of telescope in mm')
        hdr['APTAREA'] = (np.pi*(self.diameter/2)**2, 'Aperture area of telescope in mm^2')
        hdr['SBSTDVER'] = ('SBFITSEXT Version 1.0', 'Version of SBFITSEXT standard')
        hdr['HSINKT'] = (self.camera.HeatSinkTemperature, 'Heat sink temperature in C')
        hdr['EGAIN'] = (self.camera.ElectronsPerADU, 'Electronic gain in e-/ADU')
        hdr['EGAINMAX'] = (self.camera.GainMax, 'Maximum electronic gain in e-/ADU')
        hdr['EGAINMIN'] = (self.camera.GainMin, 'Minimum electronic gain in e-/ADU')
        hdr['ISSHUTTR'] = (self.camera.HasShutter, 'Whether a mechanical shutter is present')
        if self.camera.CanFastReadout: hdr['FASTREAD'] = (self.camera.FastReadout, 'Fast readout mode')
        hdr['FULLWELL'] = (self.camera.FullWellCapacity, 'Full well capacity in e-')
        hdr['MAXADU'] = (self.camera.MaxADU, 'Maximum ADU value in image')
        hdr['WIDTH'] = (self.camera.PixelSizeX, 'Width of CCD in pixels')
        hdr['HEIGHT'] = (self.camera.PixelSizeY, 'Height of CCD in pixels')
        hdr['CAMNAME'] = (self.camera.Name, 'Name of camera')
        hdr['SENSOR'] = (self.camera.SensorName, 'Name of sensor')
        try: hdr['SUBEXP'] = (self.camera.SubExposureDuration, 'Subexposure time in seconds')
        except: pass
        match self.camera.SensorType:
            case 1: hdr['BAYERPAT'] = ('Color', 'Sensor type')
            case 2: hdr['BAYERPAT'] = ('RGGB', 'Sensor type')
            case 3: hdr['BAYERPAT'] = ('CMYG', 'Sensor type')
            case 4: hdr['BAYERPAT'] = ('CMYG2', 'Sensor type')
            case 5: hdr['BAYERPAT'] = ('LRGB', 'Sensor type')
        if self.camera.SensorType != 0:
            hdr['BAYOFFX'] = (self.camera.BayerOffsetX, 'Bayer X offset')
            hdr['BAYOFFY'] = (self.camera.BayerOffsetY, 'Bayer Y offset')

        hdr['TELENAME'] = (self.telescope.Name, 'Telescope name')
        hdr['TARGET'] = (target, 'Target name')
        hdr['OBJCTALT'] = (self.telescope.Altitude, 'Telescope altitude in degrees')
        hdr['OBJCTAZ'] = (self.telescope.Azimuth, 'Telescope azimuth in degrees')
        hdr['OBJCTRA'] = (self.telescope.RightAscension, 'Telescope right ascension in hours')
        hdr['OBJCTDEC'] = (self.telescope.Declination, 'Telescope declination in degrees')
        hdr['RARATE'] = (self.telescope.RightAscensionRate, 'Telescope right ascension rate in seconds per sidereal second')
        hdr['DECRATE'] = (self.telescope.DeclinationRate, 'Telescope declination rate in arcseconds per sidereal second')
        hdr['HA'] = (self.telescope.HourAngle, 'Telescope hour angle in degrees')
        hdr['EQSYS'] (self.telescope.EquatorialSystem, 'Telescope equatorial system')
        hdr['TELELST'] = (self.telescope.SiderealTime, 'Telescope local sidereal time in hours')
        hdr['REFRACTION'] = (self.telescope.DoesRefraction, 'Does telescope account for refraction')
        hdr['SITE'] = (self.site, 'Site name')
        hdr['INSTRUME'] = (self.instrument_name, 'Instrument name') 
        hdr['DESCRIPT'] = (self.instrument_description, 'Instrument description')
        hdr['SITELAT'] = (self.latitude, 'Site latitude in degrees')
        hdr['SITELONG'] = (self.longitude, 'Site longitude in degrees')
        hdr['SITEELEV'] = (self.elevation, 'Site elevation in meters')
        hdr['TRACKING'] = (self.telescope.Tracking, 'Telescope tracking state')
        hdr['TRKRATE'] = (self.telescope.TrackingRate, 'Telescope tracking rate')

        if self.dome is not None:
            hdr['DOMENAME'] = (self.dome.Name, 'Dome name')
            hdr['DOMEALT'] = (self.dome.Altitude, 'Dome altitude in degrees')
            hdr['DOMEAZ'] = (self.dome.Azimuth, 'Dome azimuth in degrees')
            hdr['DOMESTAT'] = (self.dome.Status, 'Dome status')
        
        if self.filter_wheel is not None:
            hdr['FWNAME'] = (self.filter_wheel.Name, 'Filter wheel name')
            hdr['FILTERPS'] = (self.filter_wheel.Position, 'Filter wheel position')
            hdr['FILTER'] = (self.filters[self.filter_wheel.Position], 'Filter name')
            if self.focuser is not None:
                hdr['FOCOFFST'] = (self.filter_focus_offsets[self.filter_wheel.Position], 'Filter focus offset in steps')
        
        if self.focuser is not None:
            hdr['FOCNAME'] = (self.focuser.Name, 'Focuser name')
            hdr['FOCPOS'] = (self.focuser.Position, 'Focuser position in steps')
            hdr['FOCSTEP'] = (self.focuser.StepSize, 'Focuser step size in microns')
            hdr['FOCTEMP'] = (self.focuser.Temperature, 'Focuser temperature in C')
            if self.focuser.TempCompAvailable: hdr['TEMPCOMP'] = (self.focuser.TempComp, 'Focuser temperature compensation')
            hdr['MAXSTEP'] = (self.focuser.MaxStep, 'Maximum focuser step')

        if self.observing_conditions is not None:
            hdr['WXNAME'] = (self.observing_conditions.Name, 'Observing conditions name')
            hdr['WXAVG'] = (self.observing_conditions.AveragePeriod, 'Observing conditions average period in seconds')
            try: 
                hdr['WXCLOUDS'] = (self.observing_conditions.CloudCover, 'Cloud cover')
                hdr['WXLSTUPD'] = (self.observing_conditions.TimeSinceLastUpdate('CloudCover'), 'CloudCover last updated')
            except: pass
            try: 
                hdr['WXDEWPT'] = (self.observing_conditions.DewPoint, 'Dew point in C')
                hdr['WXLSTUPD'] = (self.observing_conditions.TimeSinceLastUpdate('DewPoint'), 'DewPoint last updated')
            except: pass
            try: 
                hdr['WXHUMID'] = (self.observing_conditions.Humidity, 'Humidity in percent')
                hdr['WXLSTUPD'] = (self.observing_conditions.TimeSinceLastUpdate('Humidity'), 'Humidity last updated')
            except: pass
            try: 
                hdr['WXPRESS'] = (self.observing_conditions.Pressure, 'Pressure in mbar')
                hdr['WXLSTUPD'] = (self.observing_conditions.TimeSinceLastUpdate('Pressure'), 'Pressure last updated')
            except: pass
            try: 
                hdr['WXRAIN'] = (self.observing_conditions.RainRate, 'Rain rate in mm/hr')
                hdr['WXLSTUPD'] = (self.observing_conditions.TimeSinceLastUpdate('RainRate'), 'RainRate last updated')
            except: pass
            try: 
                hdr['WXSKYBR'] = (self.observing_conditions.SkyBrightness, 'Sky brightness in magnitudes')
                hdr['WXLSTUPD'] = (self.observing_conditions.TimeSinceLastUpdate('SkyBrightness'), 'SkyBrightness last updated')
            except: pass
            try: 
                hdr['WXSKYQM'] = (self.observing_conditions.SkyQuality, 'Sky quality in magnitudes')
                hdr['WXLSTUPD'] = (self.observing_conditions.TimeSinceLastUpdate('SkyQuality'), 'SkyQuality last updated')
            except: pass
            try: 
                hdr['WXFWHM'] = (self.observing_condition.StarFWHM, 'Star FWHM in arcseconds')
                hdr['WXLSTUPD'] = (self.observing_conditions.TimeSinceLastUpdate('StarFWHM'), 'StarFWHM last updated')
            except: pass
            try: 
                hdr['WXTEMP'] = (self.observing_conditions.Temperature, 'Temperature in C')
                hdr['WXLSTUPD'] = (self.observing_conditions.TimeSinceLastUpdate('Temperature'), 'Temperature last updated')
            except: pass
            try: 
                hdr['WXWINDIR'] = (self.observing_conditions.WindDirection, 'Wind direction in degrees')
                hdr['WXLSTUPD'] = (self.observing_conditions.TimeSinceLastUpdate('WindDirection'), 'WindDirection last updated')
            except: pass
            try: 
                hdr['WXWINDG'] = (self.observing_conditions.WindGust, 'Wind gust in km/hr')
                hdr['WXLSTUPD'] = (self.observing_conditions.TimeSinceLastUpdate('WindGust'), 'WindGust last updated')
            except: pass
            try: 
                hdr['WXWINDSP'] = (self.observing_conditions.WindSpeed, 'Wind speed in km/hr')
                hdr['WXLSTUPD'] = (self.observing_conditions.TimeSinceLastUpdate('WindSpeed'), 'WindSpeed last updated')
            except: pass

        if self.rotator is not None:
            hdr['ROTNAME'] = (self.rotator.Name, 'Rotator name')
            hdr['ROTANGLE'] = (self.rotator.Position, 'Rotator angle in degrees')
            hdr['MECHANGL'] = (self.rotator.MechanicalPosition, 'Mechanical angle in degrees')
            # TODO: Add whether de-rotation is on
        
        if self.safety_monitor is not None:
            for i, safety_monitor in enumerate(self.safety_monitor):
                hdr['SAFNM%i' % i] = (safety_monitor.Name, 'Safety monitor name')
                hdr['SAFSTAT%i' % i] = (safety_monitor.IsSafe, 'Safety monitor status')
        
        # TODO: Add capability to optionally save switch statuses to header

        hdu = pyfits.PrimaryHDU(self.camera.ImageArray, header=hdr)
        hdu.writeto(filename, overwrite=overwrite)

        if do_wcs: self._wcs.Solve(filename, **wcs_kwargs)

        return True
    
    def slew_to_coordinates(self, obj=None, ra=None, dec=None, unit=('hr', 'deg'), frame='icrs', 
                            control_dome=False, control_rotator=False):
        '''Slews the telescope to a given ra and dec'''

        obj = self._parse_obj_ra_dec(obj, ra, dec, unit, frame)

        logging.info('Slewing to RA %i:%i:%.2f and Dec %i:%i:%.2f' % obj.ra.hms[0], obj.ra.hms[1], obj.ra.hms[2],
            obj.dec.dms[0], obj.dec.dms[1], obj.dec.dms[2])
        slew_obj = self.get_object_slew(obj)
        altaz_obj = self.get_object_altaz(obj)

        if not self.telescope.Connected: raise ObservatoryException('The telescope is not connected.')

        if altaz_obj.alt.deg <= self.min_altitude:
            logging.warning('Target is below the minimum altitude of %.2f degrees' % self.min_altitude)
            return False
        
        if self.telescope.CanPark:
            if self.telescope.AtPark:
                logging.info('Telescope is parked, unparking...')
                self.telescope.Unpark()
                if self.telescope.CanFindHome:
                    logging.info('Finding home position...')
                    self.telescope.FindHome()
        
        logging.info('Attempting to slew to coordinates...')
        if self.telescope.CanSlew: 
            if self.telescope.CanSlewAsync: self.telescope.SlewToCoordinatesAsync(slew_obj.ra.hour, slew_obj.dec.deg)
            else: self.telescope.SlewToCoordinates(slew_obj.ra.hour, slew_obj.dec.deg)
        elif self.telescope.CanSlewAltAz:
            if self.telescope.CanSlewAltAzAsync: self.telescope.SlewToAltAzAsync(altaz_obj.alt.deg, altaz_obj.az.deg)
            else: self.telescope.SlewToAltAz(altaz_obj.alt.deg, altaz_obj.az.deg)
        else: raise ObservatoryException('The telescope cannot slew to coordinates.')

        if control_dome and self.dome is not None:
            if self.dome.ShutterState != 0 and self.CanSetShutter:
                logging.info('Opening the dome shutter...')
                self.dome.OpenShutter()
                if self.dome.CanFindHome:
                    logging.info('Finding the dome home...')
                    self.dome.FindHome()
            if self.dome.CanPark:
                if self.dome.AtPark and self.dome.CanFindHome:
                    logging.info('Finding the dome home...')
                    self.dome.FindHome()
            if not self.dome.Slaved:
                if self.dome.CanSetAltitude: 
                    logging.info('Setting the dome altitude...')
                    self.dome.SlewToAltitude(altaz_obj.alt.deg)
                if self.dome.CanSetAzimuth: 
                    logging.info('Setting the dome azimuth...')
                    self.dome.SlewToAzimuth(altaz_obj.az.deg)
        
        if control_rotator and self.rotator is not None:
            self.stop_derotation()

            rotation_angle = (self.lst() - slew_obj.ra.hour) * 15

            if (self.rotator.MechanicalPosition + rotation_angle >= self.rotator_max_angle or
                self.rotator.MechanicalPosition - rotation_angle <= self.rotator_min_angle):
                logging.warning('Rotator will pass through the limit. Cannot slew to target.')
                return False

            logging.info('Rotating the rotator to hour angle %.2f' % hour_angle)
            self.rotator.MoveAbsolute(rotation_angle)

        condition = True
        while condition:
            condition = self.telescope.Slewing
            if self.control_dome and self.dome is not None: condition = condition or self.dome.Slewing
            if self.control_rotator and self.rotator is not None: condition = condition or self.rotator.IsMoving
            time.sleep(0.1)
        logging.info('Slew complete')

        if self.telescope.CanSetTracking: 
            logging.info('Turning on sidereal tracking...')
            self.telescope.TrackingRate = 0
            self.telescope.Tracking = True
            logging.info('Sidereal tracking is on.')
        else: logging.warning('Tracking cannot be turned on.')

        if self.control_rotator and self.rotator is not None: 
            logging.info('Starting derotation...')
            self.derotate()

        return True

    def derotate(self):
        '''Begin a derotation thread for the current ra and dec'''
        return
    
    def stop_derotation(self):
        '''Stops the derotation thread'''
        return

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
    
    def autofocus(self):
        '''Runs the autofocus routine'''
        return
    
    def recenter(self, obj=None, ra=None, dec=None, unit=('hr', 'deg'), frame='icrs', target_x_pixel=None, 
                target_y_pixel=None, initial_offset_dec=0, check_and_refine=True, max_attempts=5, tolerance=3, 
                exposure=10, save_images=False, save_path='./', sync_mount=False, settle_time=5, do_initial_slew=True):
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

        logging.info('Attempting to put %s RA %i:%i:%.2f and Dec %i:%i:%.2f on pixel (%.2f, %.2f)' %
            (frame, obj.ra.hms[0], obj.ra.hms[1], obj.ra.hms[2], obj.dec.dms[0], obj.dec.dms[1], obj.dec.dms[2], 
            target_x_pixel, target_y_pixel))

        if initial_offset_dec != 0 and do_initial_slew:
            logging.info('Offseting the initial slew declination by %.2f arcseconds' % initial_offset_dec)

        for attempt in range(max_attempts):
            slew_obj = self.get_object_slew(obj)
            
            if check_and_refine:
                logging.info('Attempt %i of %i' % (attempt+1, max_attempts))
            
            if attempt == 0: 
                if do_initial_slew:
                    if initial_offset_dec != 0:
                        logging.info('Offseting the initial slew declination by %.2f arcseconds' % initial_offset_dec)
                    self.slew_to_coordinates(slew_obj.ra.hour, slew_obj.dec.deg + initial_offset_dec/3600)
            else: self.slew_to_coordinates(slew_obj.ra.hour, slew_obj.dec.deg)
            
            logging.info('Settling for %.2f seconds' % settle_time)
            time.sleep(settle_time)

            if not check_and_refine and attempt_number > 0:
                logging.info('Check and recenter is off, single-shot recentering complete')
                return True
            
            logging.info('Refreshing observing conditions')
            self.observing_conditions.Refesh()

            logging.info('Taking %.2f second exposure' % exposure)
            self.camera.ReadoutMode = self.camera.ReadoutModes[self.default_readout_mode]
            self.camera.StartExposure(exposure, True)
            while not self.camera.ImageReady: time.sleep(0.1)
            logging.info('Exposure complete')

            temp_image = tempfile.gettempdir()+'%s.fts' % astrotime.Time(self.observatory_time, format='fits').value
            self.save_last_image(temp_image)

            logging.info('Searching for a WCS solution...')
            solution_found = self._wcs.Solve(temp_image, ra_key='OBJCTRA', dec_key='OBJCTDEC', 
                                            ra_dec_units=('hour', 'deg'), solve_timeout=60, 
                                            scale_units='arcsecperpix', scale_type='ev',
                                            scale_est=self.pixel_scale[0], scale_err=self.pixel_scale[0]*0.1,
                                            parity=1, crpix_center=True)

            if save_images:
                logging.info('Saving the centering image to %s' % save_path)
                shutil.copy(temp_image, save_path)

            if not solution_found:
                logging.info('No WCS solution found, skipping this attempt')
                continue
            
            logging.info('WCS solution found, solving for the pixel location of the target')
            try:
                hdulist = pyfits.open(temp_image)
                w = astropy.wcs.WCS(hdulist[0].header)

                center_coord = w.pixel_to_world(int(self.camera.CameraXSize/2), int(self.camera.CameraYSize/2))
                center_ra = center_coord.ra.hour; center_dec = center_coord.dec.deg
                logging.info('Center of the image is at RA %i:%i:%.2f and Dec %i:%i:%.2f' % 
                    (center_coord.ra.hms[0], center_coord.ra.hms[1], center_coord.ra.hms[2],
                    center_coord.dec.dms[0], center_coord.dec.dms[1], center_coord.dec.dms[2]))

                coord = w.pixel_to_world(target_x_pixel, target_y_pixel)
                target_pixel_ra = coord.ra.hour; target_pixel_dec = coord.dec.deg
                logging.info('Target is at RA %i:%i:%.2f and Dec %i:%i:%.2f' % 
                (coord.ra.hms[0], coord.ra.hms[1], coord.ra.hms[2],
                coord.dec.dms[0], coord.dec.dms[1], coord.dec.dms[2]))

                pixels = w.world_to_pixel(obj)
                obj_x_pixel = pixels[0]; obj_y_pixel = pixels[1]
                logging.info('Object is at pixel (%.2f, %.2f)' % (obj_x_pixel, obj_y_pixel))
            except: 
                logging.info('Could not solve for the pixel location of the target, skipping this attempt')
                continue

            error_ra = obj.ra.hour - target_pixel_ra; error_dec = obj.dec.deg - target_pixel_dec
            error_x_pixels = obj_x_pixel - target_x_pixel; error_y_pixels = obj_y_pixel - target_y_pixel
            logging.info('Error in RA is %.2f arcseconds' % (error_ra*15*3600))
            logging.info('Error in Dec is %.2f arcseconds' % (error_dec*3600))
            logging.info('Error in x pixels is %.2f' % error_x_pixels)
            logging.info('Error in y pixels is %.2f' % error_y_pixels)

            if max(error_x_pixels, error_y_pixels) <= max_pixel_error:
                break

            logging.info('Offsetting next slew coordinates')
            obj = self._parse_obj_ra_dec(ra=obj.ra.hour + error_ra, dec=obj.dec.deg + error_dec, 
                                unit=('hour', 'deg'), frame='icrs')
        else:
            logging.info('Target could not be centered after %d attempts' % max_attempts)
            return False
        
        if sync_mount:
                logging.info('Syncing the mount to the center ra and dec transformed to J-Now...')

                sync_obj = self._parse_obj_ra_dec(ra=center_ra, dec=center_dec, unit=('hour', 'deg'), frame='icrs')
                sync_obj = self.get_object_slew(sync_obj)
                self.telescope.SyncToCoordinates(sync_obj.ra.hour, sync_obj.dec.deg)
                logging.info('Sync complete')
            
        logging.info('Target is now in position after %d attempts' % (attempt+1))

        return True
    
    def take_flats(self, filter_exposure, filter_brightness=None, readouts=None, binnings=(1, 1), 
        repeat=10, save_path=None, new_folder=None, home_telescope=False, 
        final_telescope_position='no change'):
        '''Takes a sequence of flat frames'''

        logging.info('Taking flat frames')

        if self.filter_wheel is None or self.cover_calibrator is None:
            logging.info('Filter wheel or cover calibrator is not available, exiting')
            return False

        if len(filter_exposure) != len(self.filters):
            logging.info('Number of filter exposures does not match the number of filters, exiting')
            return False
        
        if save_path is None:
            save_path = os.getcwd()
            logging.info('Setting save path to current working directory: %s' % save_path)
        
        if type(new_folder) is bool:
            save_path = os.path.join(save_path, datetime.datetime.now().strftime('Flats_%Y-%m-%d_%H-%M-%S'))
            os.makedirs(save_path)
            logging.info('Created new directory: %s' % save_path)
        elif type(new_folder) is str:
            save_path = os.path.join(save_path, new_folder)
            os.makedirs(save_path)
            logging.info('Created new directory: %s' % save_path)

        if home_telescope and self.telescope.CanFindHome:
            logging.info('Homing the telescope')
            self.telescope.FindHome()
            logging.info('Homing complete')

        logging.info('Slewing to point at cover calibrator')
        self.telescope.SlewToAltAz(self.cover_calibrator_az, self.cover_calibrator_alt)
        self.telescope.Tracking = False
        logging.info('Slew complete')

        if self.cover_calibrator.CoverState != 'NotPresent':
            logging.info('Opening the cover calibrator')
            self.cover_calibrator.OpenCover()
            logging.info('Cover open')

        for i in range(len(self.filters)):
            if filter_exposure[i] == 0: continue
            for readout in readouts:
                self.camera.ReadoutMode = readout
                for binning in binnings:
                    if type(binnings[0]) is tuple: self.camera.BinX = binning[0]; self.camera.BinY = binning[1]
                    else: self.camera.BinX = binning; self.camera.BinY = binning
                    for j in range(repeat):
                        while self.camera.Temperature > (self.cooler_setpoint + self.cooler_tolerance):
                            logging.info('Cooler is not at setpoint, waiting 10 seconds...')
                            time.sleep(10)
                        self.filter_wheel.Position = i
                        if self.cover_calibrator.CalibratorState != 'NotPresent' or filter_brightness is not None:
                            logging.info('Setting the cover calibrator brightness to %i' % filter_brightness[i])
                            self.cover_calibrator.CalibratorOn(filter_brightness[i])
                        camera.StartExposure(filter_exposure[i], False)
                        save_string = save_path + ('flat_%s_%ix%i_%4.4f_%i_%i.fts' % 
                            (self.filters[i], self.camera.BinX, self.camera.BinY, filter_exposure[i], 
                            self.camera.ReadoutModes[self.camera.ReadoutMode].replace(' ', ''), j))
                        while not camera.ImageReady:
                            time.sleep(0.1)
                        self.save_last_image(save_string, frametyp='Flat')
                        logging.info('Flat %i of %i complete: %s' % (j, repeat, save_string))
        
        if self.cover_calibrator.CalibratorState != 'NotPresent':
            logging.info('Turning off the cover calibrator')
            self.cover_calibrator.CalibratorOff()
            logging.info('Cover calibrator off')
            
        if self.cover_calibrator.CoverState != 'NotPresent':
            logging.info('Closing the cover calibrator')
            self.cover_calibrator.CloseCover()
            logging.info('Cover closed')

            if final_telescope_position == 'no change':
                logging.info('No change to telescope position requested, exiting')
            elif final_telescope_position == 'home' and self.telescope.CanFindHome:
                logging.info('Homing the telescope')
                self.telescope.FindHome()
                logging.info('Homing complete')
            elif final_telescope_position == 'park' and self.telescope.CanPark:
                logging.info('Parking the telescope')
                self.telescope.Park()
                logging.info('Parking complete')
            
        logging.info('Flats complete')

        return True
    
    def take_darks(self, exposures, readouts, binnings, repeat=10, save_path=None, new_folder=None):
        '''Takes a sequence of dark frames'''

        logging.info('Taking dark frames')

        if save_path is None:
            save_path = os.getcwd()
            logging.info('Setting save path to current working directory: %s' % save_path)
        
        if type(new_folder) is bool:
            save_path = os.path.join(save_path, datetime.datetime.now().strftime('Flats_%Y-%m-%d_%H-%M-%S'))
            os.makedirs(save_path)
            logging.info('Created new directory: %s' % save_path)
        elif type(new_folder) is str:
            save_path = os.path.join(save_path, new_folder)
            os.makedirs(save_path)
            logging.info('Created new directory: %s' % save_path)

        for exposure in exposures:
            for readout in readouts:
                self.camera.ReadoutMode = readout
                for binning in binnings:
                    if type(binnings[0]) is tuple: self.camera.BinX = binning[0]; self.camera.BinY = binning[1]
                    else: self.camera.BinX = binning; self.camera.BinY = binning
                    for j in range(repeat):
                        while self.camera.Temperature > (self.cooler_setpoint + self.cooler_tolerance):
                            logging.info('Cooler is not at setpoint, waiting 10 seconds...')
                            time.sleep(10)
                        camera.StartExposure(exposure, False)
                        save_string = save_path + ('dark_%s_%ix%i_%4.4gs__%i.fts' % (
                                self.camera.ReadoutModes[self.camera.ReadoutMode].replace(' ', ''),
                                self.camera.BinX, self.camera.BinY, 
                                exposure, j))
                        while not camera.ImageReady:
                            time.sleep(0.1)
                        self.save_last_image(save_string, frametyp='Dark')
                        logging.info('Dark %i of %i complete: %s' % (j, repeat, save_string))
        
        logging.info('Darks complete')

        return True

    def save_config(self, filename):
        with open(filename, 'w') as configfile:
            self.config.write(configfile)
    
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
        self.default_readout_mode = dictionary.get('default_readout_mode', self.default_readout_mode)

        self.cover_calibrator_alt = dictionary.get('cover_calibrator_alt', self.cover_calibrator_alt)
        self.cover_calibrator_az = dictionary.get('cover_calibrator_az', self.cover_calibrator_az)

        self.filters = dictionary.get('filters', self.filters)
        self.filter_focus_offsets = dictionary.get('filter_focus_offsets', self.filter_focus_offsets)

        self.focuser_max_error = dictionary.get('focuser_max_error', self.focuser_max_error)

        self.rotator_reverse = dictionary.get('rotator_reverse', self.rotator_reverse)
        self.rotator_min_angle = dictionary.get('rotator_min_angle', self.rotator_min_angle)
        self.rotator_max_angle = dictionary.get('rotator_max_angle', self.rotator_max_angle)

        self.min_altitude = dictionary.get('min_altitude', self.min_altitude)

        self.autofocus_exposure = dictionary.get('autofocus_exposure', self.autofocus_exposure)
        self.autofocus_start_position = dictionary.get('autofocus_start_position', self.autofocus_start_position)
        self.autofocus_step_number = dictionary.get('autofocus_step_number', self.autofocus_step_number)
        self.autofocus_step_size = dictionary.get('autofocus_step_size', self.autofocus_step_size)
        self.autofocus_use_current_pointing = dictionary.get('autofocus_use_current_pointing', self.autofocus_use_current_pointing)

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
    def default_readout_mode(self):
        return self._default_readout_mode
    @default_readout_mode.setter
    def default_readout_mode(self, value):
        self._default_readout_mode = int(value) if value is not None or value !='' else None
        self._config['camera']['default_readout_mode'] = str(self._default_readout_mode) if self._default_readout_mode is not None else ''

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
    def wcs_driver(self):
        return self._wcs_driver

    @property
    def last_camera_shutter_status(self):
        return self._last_camera_shutter_status

class ObservatoryException(Exception):
    pass