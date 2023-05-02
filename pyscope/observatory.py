from astropy import coordinates as coord, time as Time
import astropy.wcs, astropy.io.fits as pyfits
import configparser
import logging
import tempfile
import shutil

from . import Autofocus, Camera, CoverCalibrator, Dome, FilterWheel, Focuser, ObservingConditions
from . import Rotator, SafetyMonitor, Switch, Telescope, WCS
from . import _check_class_inheritance

import drivers._ascom.Driver as AscomDriver

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
        self._config['telescope'] = {}; self._config['autofocus'] = {}; self._config['calibration'] = {}
        self._config['recenter'] = {}

        self.site_name = 'pyScope Site'
        self.instrument_name = 'pyScope Instrument' 
        self.instrument_description = 'pyScope is a pure-Python telescope control package.'
        self.get_site_from_telescope = False
        self.latitude = None; self.longitude = None; self.elevation = None
        self.diameter = None; self.focal_length = None

        self._camera = None
        self.cooler_setpoint = None; self.cooler_tolerance = None; self.max_dimension = None
        self.pixel_x_size = None; self.pixel_y_size = None; self.default_readout_mode = None

        self._cover_calibrator = None
        self.cover_calibrator_alt = None; self.cover_calibrator_az = None

        self._dome = None

        self._filter_wheel = None
        self.filters = None; self.filter_focus_offsets = None; self.autofocus_filters = None
        self.recentering_filters = None; self.wcs_filters = None

        self._focuser = None
        self.focuser_max_error = 10

        self._observing_conditions = None

        self._rotator = None
        self.rotator_min_angle = None; self.rotator_max_angle = None

        self._safety_monitor = None

        self._switch = None

        self._telescope = None
        self.min_altitude = 10

        self._autofocus = None
        self.autofocus_exposure = 10; self.autofocus_start_position = None; self.autofocus_step_number = 5;
        self.autofocus_step_size = 500; self.autofocus_use_current_pointing = True

        self.calibration_filter_exposure = None; self.calibration_filter_focus = None

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
            self._wcs_driver = self.config.get('recenter', 'wcs_driver', fallback=None)
            self._wcs = WCS(self.wcs_driver)

            # Get other keywords from config file
            master_dict = {**self._config['site'], **self._config['camera'], **self._config['cover_calibrator'],
                **self._config['dome'], **self._config['filter_wheel'], **self._config['focuser'],
                **self._config['observing_conditions'], **self._config['rotator'], **self._config['safety_monitor'],
                **self._config['switch'], **self._config['telescope'], **self._config['autofocus'], 
                **self._config['calibration'], **self._config['recenter']}
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
    
    def shutdown(self):
        '''Shuts down the observatory'''
        return
    
    def autofocus(self):
        '''Runs the autofocus routine'''
        return

    def take_flat_sequence(self):
        '''Takes a sequence of flat frames defined by the calibration configuration'''
        return
    
    def take_dark_sequence(self):
        '''Takes a sequence of dark frames'''
        return
    
    def recenter(self, obj=None, ra=None, dec=None, unit=('hr', 'deg'), frame='icrs', target_x_pixel=None, 
                target_y_pixel=None, initial_offset_dec=0, check_and_refine=True, max_attempts=5, tolerance=3, 
                exposure=10, save_images=False, save_path='.', sync_mount=False, settle_time=5, do_initial_slew=True):
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

        if type(obj) is str: obj = coord.SkyCoord.from_name(obj)
        elif type(obj) is coord.SkyCoord: pass
        elif ra is not None and dec is not None: obj = coord.SkyCoord(ra=ra, 
            dec=dec, unit=unit, frame=frame)

        if obj is None: raise Exception('Either the object, the ra, or the dec must be specified.')

        logging.info('Attempting to put %s RA %i:%i:%.2f and Dec %i:%i:%.2f on pixel (%.2f, %.2f)' %
            (frame, obj.ra.hms[0], obj.ra.hms[1], obj.ra.hms[2], obj.dec.dms[0], obj.dec.dms[1], obj.dec.dms[2], 
            target_x_pixel, target_y_pixel))

        if initial_offset_dec != 0 and do_initial_slew:
            logging.info('Offseting the initial slew declination by %.2f arcseconds' % initial_offset_dec)

        for attempt in range(max_attempts):
            slew_obj = obj.transform_to(coord.TETE(obstime=time.Time.now(), location=self.earth_location))
            
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
            
            logging.info('Taking %.2f second exposure' % exposure)
            self.camera.StartExposure(exposure, True)
            while not self.camera.ImageReady: time.sleep(0.1)
            logging.info('Exposure complete')

            temp_image = tempfile.gettempdir()+'temp.fts' % attempt_number
            self.save_image(temp_image)

            logging.info('Searching for a WCS solution...')
            solution_found = self.WCS.Solve(temp_image)

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
            obj = coord.SkyCoord(ra=obj.ra.hour + error_ra, dec=obj.dec.deg + error_dec, 
                                unit=('hour', 'deg'), frame='icrs')
        else:
            logging.info('Target could not be centered after %d attempts' % max_attempts)
            return False
        
        if sync_mount:
                logging.info('Syncing the mount to the center ra and dec transformed to J-Now...')

                sync_obj = coord.SkyCoord(ra=center_ra, dec=center_dec, unit=('hour', 'deg'), frame='icrs')
                sync_obj = sync_obj.transform_to(coord.TETE(obstime=time.Time.now(), location=self.earth_location))
                self.telescope.SyncToCoordinates(sync_obj.ra.hour, sync_obj.dec.deg)
                logging.info('Sync complete')
            
        logging.info('Target is now in position after %d attempts' % (attempt+1))
        return True
    
    def slew_to_coordinates(self, ra, dec):
        '''Slews the telescope to a given ra and dec'''
        return
    
    def derotate(self):
        '''Begin a derotation thread for the current ra and dec'''
        return
    
    def stop_derotation(self):
        '''Stops the derotation thread'''
        return
    
    def safety_status(self):
        '''Returns the status of the safety monitors'''
        return
    
    def switch_status(self):
        '''Returns the status of the switches'''
        return
    
    def save_image(self, filename):
        '''Saves the current image'''
        return

    def save_config(self, filename=None):
        with open(filename, 'w') as configfile:
            self.config.write(configfile)
    
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
        self.default_readout_mode = dictionary.get('default_readout_mode', self.default_readout_mode)

        self.cover_calibrator_alt = dictionary.get('cover_calibrator_alt', self.cover_calibrator_alt)
        self.cover_calibrator_az = dictionary.get('cover_calibrator_az', self.cover_calibrator_az)

        self.filters = dictionary.get('filters', self.filters)
        self.filter_focus_offsets = dictionary.get('filter_focus_offsets', self.filter_focus_offsets)
        self.autofocus_filters = dictionary.get('autofocus_filters', self.autofocus_filters)
        self.recentering_filters = dictionary.get('recentering_filters', self.recentering_filters)
        self.wcs_filters = dictionary.get('wcs_filters', self.wcs_filters)

        self.focuser_max_error = dictionary.get('focuser_max_error', self.focuser_max_error)

        self.rotator_min_angle = dictionary.get('rotator_min_angle', self.rotator_min_angle)
        self.rotator_max_angle = dictionary.get('rotator_max_angle', self.rotator_max_angle)

        self.min_altitude = dictionary.get('min_altitude', self.min_altitude)

        self.autofocus_exposure = dictionary.get('autofocus_exposure', self.autofocus_exposure)
        self.autofocus_start_position = dictionary.get('autofocus_start_position', self.autofocus_start_position)
        self.autofocus_step_number = dictionary.get('autofocus_step_number', self.autofocus_step_number)
        self.autofocus_step_size = dictionary.get('autofocus_step_size', self.autofocus_step_size)
        self.autofocus_use_current_pointing = dictionary.get('autofocus_use_current_pointing', self.autofocus_use_current_pointing)

        self.calibration_filter_exposure = dictionary.get('calibration_filter_exposure', self.calibration_filter_exposure)
        self.calibration_filter_timeout = dictionary.get('calibration_filter_timeout', self.calibration_filter_timeout)

    @property
    def earth_location(self):
        '''Returns the EarthLocation object for the observatory'''
        return coord.EarthLocation(lat=self.latitude, lon=self.longitude, height=self.elevation)

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
    def wcs_driver(self):
        return self._wcs_driver

class ObservatoryException(Exception):
    pass