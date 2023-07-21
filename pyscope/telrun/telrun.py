import atexit
import configparser
import os
import shutil
import threading

from astropy import coordinates as coord

from pyscope import Observatory, logger

class TelrunOperator:
    def __init__(self, config_file_path=None, gui=False, **kwargs):

        # Non-accessible variables
        self._config = configparser.ConfigParser()
        self._gui = None
        self._telrun_file = None
        self._best_focus_result = None
        self._hardware_status = None
        self._wcs_thread = []
        
        # Read-only variables
        self._telhome = None
        self._observatory = None
        self._dome_type = None # None, 'dome' or 'safety-monitor' or 'both
        self._do_periodic_autofocus = False
        self._last_autofocus_time = None
        self._skipped_scan_count = 0
        self._current_scan = None
        self._current_scan_index = None
        self._previous_scan = None
        self._previous_scan_index = None
        self._next_scan = None
        self._next_scan_index = None

        # Read/write variables
        self._initial_home = True
        self._wait_for_sun = True
        self._max_solar_elev = -12
        self._check_safety_monitors = True
        self._wait_for_cooldown = True
        self._default_readout = 0
        self._autofocus_interval = 3600
        self._initial_autofocus = True
        self._autofocus_filters = None
        self._autofocus_exposure = 5
        self._autofocus_midpoint = 0
        self._autofocus_nsteps = 5
        self._autofocus_step_size = 500
        self._autofocus_use_current_pointing = False
        self._autofocus_timeout = 180
        self._wait_for_scan_start_time = True
        self._max_scan_late_time = 60
        self._preslew_time = 60
        self._recenter_filters = None
        self._recenter_initial_offset_dec = 0
        self._recenter_check_and_refine = True
        self._recenter_max_attempts = 5
        self._recenter_tolerance = 3
        self._recenter_exposure = 10
        self._recenter_save_images = False
        self._recenter_save_path = self.telhome + '/images/recenter/'
        self._recenter_sync_mount = False
        self._hardware_timeout = 120
        self._wcs_filters = None
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
    
    def save_config(self, filename):
        save_dir = self.telhome + '/config/'
        self.observatory.save_config(save_dir+'observatory.cfg')
        self._config['observatory'] = save_dir+'observatory.cfg'
        with open(save_dir + filename, 'w') as config_file:
            self._config.write(config_file)

    def generate_summary_report(self, filename):
        pass

    def run(self):
        logger.info('Checking for an existing telrun.sls file')
        if os.path.isfile(self.telhome + '/schedules/telrun.sls'):
            logger.info('Loading existing telrun.sls')
            self._telrun_file = TelrunFile(self.telhome + '/schedules/telrun.sls')

        if self.observatory.observing_conditions is not None:
            logger.info('Starting the observing_conditions update thread...')
            self.observatory.start_observing_conditions_thread()
            logger.info('Started.')

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
        
        if self._initial_home and self.observatory.telescope.CanFindHome:
            logger.info('Finding telescope home...')
            self.observatory.telescope.FindHome()
            logger.info('Found.')

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
            case 'both':
                logger.info('Checking first safety monitor status...')
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
                else:
                    logger.info('Safety monitor not found, continuing...')
                
                logger.info('Checking dome status...')
                if self.observatory.dome is not None:
                    if self.observatory.dome.CanSetShutter:
                        logger.info('Opening the dome shutter...')
                        self.observatory.dome.OpenShutter()
                        logger.info('Opened.')
                    if self.observatory.dome.CanFindHome:
                        logger.info('Finding the dome home...')
                        self.observatory.dome.FindHome()
                        logger.info('Found.')
        
        # Wait for cooler?
        while (self.observatory.camera.CCDTemperature > 
                self.observatory.cooler_setpoint + self.observatory.cooler_tolerance
                and self.wait_for_cooldown):
            logger.info('CCD temperature: %.3f degs (above limit of %.3f with %.3f tolerance)' % (
                self.observatory.camera.CCDTemperature,
                self.observatory.cooler_setpoint, 
                self.observatory.cooler_tolerance))
            time.sleep(10)
        logger.info('CCD temperature: %.3f degs (below limit of %.3f with %.3f tolerance), continuing...' % (
            self.observatory.camera.CCDTemperature,
            self.observatory.cooler_setpoint,
            self.observatory.cooler_tolerance))

        # Initial autofocus?
        if self.autofocus_interval > 0:
            self._do_periodic_autofocus = True

        if self.initial_autofocus and self.do_periodic_autofocus:
            self._last_autofocus_time = time.time() - self.autofocus_interval - 1
        
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

        logger.info('Starting scan loop...')
        for scan, scan_index in enumerate(self._telrun_file.scans):
            # Check 1: New telrun file?
            if os.path.isfile(self.telhome + '/schedules/telrun.new'):
                logger.info('Found telrun.new, ending scan loop preemptively')
                return False
            
            self._current_scan = scan
            self._current_scan_index = scan_index
            
            if scan_index != 0:
                self._previous_scan = self._telrun_file.scans[scan_index-1]
                self._previous_scan_index = scan_index-1
            else:
                self._previous_scan = None
                self._previous_scan_index = None
            
            if scan_index != len(self._telrun_file.scans)-1:
                self._next_scan = self._telrun_file.scans[scan_index+1]
                self._next_scan_index = scan_index+1
            else:
                self._next_scan = None
                self._next_scan_index = None
            
            logger.info('Processing scan %i of %i' % (scan_index+1, len(self._telrun_file.scans)))
            logger.info(scan)
        
            if scan.status != 'N':
                logger.info('Scan status is not N, skipping...')
                self._set_scan_status(scan, 'F', message='Scan already attempted to be processed')
                continue
        
            # Check 2: Wait for scan start time?
            seconds_until_start_time = time.time() - scan.start_time
            if not self.wait_for_scan_start_time and seconds_until_start_time < self.max_scan_late_time:
                logger.info('Ignoring scan start time, continuing...')
            elif not self.wait_for_scan_start_time and seconds_until_start_time > self.max_scan_late_time:
                logger.info('Ignoring scan start time, however \
                    scan start time exceeded max_scan_late_time of %i seconds, skipping...' % self.max_scan_late_time)
                self._set_scan_status(scan, 'F', message='Exceeded max_scan_late_time')
                continue
            elif self.wait_for_scan_start_time and seconds_until_start_time > self.max_scan_late_time:
                logger.info('Scan start time exceeded max_scan_late_time of %i seconds, skipping...' % self.max_scan_late_time)
                self._set_scan_status(scan, 'F', message='Exceeded max_scan_late_time')
                continue
            else:
                logger.info('Waiting %.1f seconds (%.2f hours) for scan start time...' % (
                    seconds_until_start_time, seconds_until_start_time/3600))
            
            while self.wait_for_scan_start_time and seconds_until_start_time > self.preslew_time:
                time.sleep(0.1)
                seconds_until_start_time = time.time() - scan.start_time
            else:
                if seconds_until_start_time > 0:
                    logger.info('Scan start time in %.1f seconds' % seconds_until_start_time)
            
            # Check 3: Dome status?
            match self.dome_type:
                case 'dome':
                    if self.observatory.dome is not None and self.observatory.dome.CanSetShutter:
                        if self.observatory.dome.ShutterStatus != 0:
                            logger.info('Dome shutter is not open, skipping...')
                            self._set_scan_status(scan, 'F', message='Dome shutter is not open')
                            continue
                
                case 'safety-monitor' | 'safety_monitor' | 'safetymonitor' | 'safety monitor':
                    if self.observatory.safety_monitor is not None:
                        status = False
                        if self.observatory.safety_monitor is not (iter, tuple, list):
                            status = self.observatory.safety_monitor.IsSafe
                        else:
                            status = self.observatory.safety_monitor[0].IsSafe
                        if not status:
                            logger.info('Safety monitor indicates unsafe, skipping...')
                            self._set_scan_status(scan, 'F', message='Dome safety monitor indicates unsafe')
                            continue
                
                case 'both':
                    if self.observatory.safety_monitor is not None:
                        status = False
                        if self.observatory.safety_monitor is not (iter, tuple, list):
                            status = self.observatory.safety_monitor.IsSafe
                        else:
                            status = self.observatory.safety_monitor[0].IsSafe
                        if not status:
                            logger.info('Safety monitor indicates unsafe, skipping...')
                            self._set_scan_status(scan, 'F', message='Dome safety monitor indicates unsafe')
                            continue
                    
                    if self.observatory.dome is not None and self.observatory.dome.CanSetShutter:
                        if self.observatory.dome.ShutterStatus != 0:
                            logger.info('Dome shutter is not open, skipping...')
                            self._set_scan_status(scan, 'F', message='Dome shutter is not open')
                            continue
            
            # Check 4: Check safety monitors?
            if self.check_safety_monitors:
                logger.info('Checking safety monitor statuses')

                status = True
                if type(self.observatory.safety_monitor) not in (iter, list, tuple):
                    status = self.observatory.safety_monitor.IsSafe()
                else:
                    for monitor in self.observatory.safety_monitor:
                        status = status and monitor.IsSafe()
                
                if not status:
                    logger.info('Safety monitor indicates unsafe, skipping...')
                    self._set_scan_status(scan, 'F', message='Safety monitor indicates unsafe')
                    continue
            
            # Check 5: Wait for sun?
            sun_alt_degs = self.observatory.sun_altaz()[0]
            if self.wait_for_sun and sun_alt_degs > self.max_solar_elev:
                logger.info('Sun altitude: %.3f degs (above limit of %s), skipping...' % (
                    sun_alt_degs, self.max_solar_elev))
                self._set_scan_status(scan, 'F', message='Sun altitude above limit')
                continue

            # Check 6: Is autofocus needed?
            self._best_focus_result = None
            if self.observatory.focuser is not None and self.do_periodic_autofocus and time.time() - self.last_autofocus_time > self.autofocus_interval and scan.interrupt_allowed:
                logger.info('Autofocus interval of %.2f hours exceeded, performing autofocus...' % (
                    self.autofocus_interval/3600))
                
                if self.observatory.filter_wheel is not None and self.autofocus_filters is not None:
                    if self.observatory.filters[self.observatory.filter_wheel.Position] not in self.autofocus_filters:
                        logger.info('Current filter not in autofocus filters, switching to the next filter...')

                        for i in range(self.observatory.filter_wheel.Position+1, len(self.observatory.filters)):
                            if self.observatory.filters[i] in self.autofocus_filters:
                                self.observatory.set_filter_offset_focuser(filter_name=self.observatory.filters[i])
                                break
                        else:
                            for i in range(self.observatory.filter_wheel.Position-1):
                                if self.observatory.filters[i] in self.autofocus_filters:
                                    self.observatory.set_filter_offset_focuser(filter_name=self.observatory.filters[i])
                                    break
                            else:
                                raise TelrunError('No filters in filter wheel are autofocus filters')

                self.observatory.camera.ReadoutMode = self.default_readout

                t = threading.Thread(target=self._is_process_complete, 
                    args=(self._best_focus_result, self.autofocus_timeout),
                    daemon=True, name='is_autofocus_done_thread')
                t.start()

                self._best_focus_result = self.observatory.run_autofocus(
                    exposure=self.autofocus_exposure,
                    midpoint=self.autofocus_midpoint,
                    nsteps=self.autofocus_nsteps,
                    step_size=self.autofocus_step_size,
                    use_current_pointing=self.autofocus_use_current_pointing)
                
                if best_focus_result is None:
                    logger.warning('Autofocus failed, will try again on next scan')
                else:
                    self._last_autofocus_time = time.time()
            
            # Check 7: Camera temperature
            while (self.observatory.camera.CCDTemperature > 
                self.observatory.cooler_setpoint + self.observatory.cooler_tolerance
                and self.wait_for_cooldown):
                logger.info('CCD temperature: %.3f degs (above limit of %.3f with %.3f tolerance)' % (
                    self.observatory.camera.CCDTemperature,
                    self.observatory.cooler_setpoint, 
                    self.observatory.cooler_tolerance))
                time.sleep(10)
            logger.info('CCD temperature: %.3f degs (below limit of %.3f with %.3f tolerance), continuing...' % (
                self.observatory.camera.CCDTemperature,
                self.observatory.cooler_setpoint,
                self.observatory.cooler_tolerance))

            # Checks passed: proceed with observing
            source = coord.SkyCoord(ra=scan.ra, dec=scan.dec, frame='icrs', unit=('hourangle', 'deg'), 
                                    pm_ra_cosdec=scan.pm_ra_cosdec, pm_dec=scan.pm_dec)
            
            # Is the previous target different?
            slew = True
            if self.previous_scan is not None:
                if (self.previous_scan.ra == scan.ra 
                        and self.previous_scan.dec == scan.dec
                        and self.previous_scan.status == 'D'
                        and best_focus_result is not None):
                    logger.info('Previous target is same ra and dec, skipping initial slew...')
                    slew = False
            
            # Perform centering if requested
            centered = None
            if None not in (scan.posx, scan.posy):
                logger.info('Refining telescope pointing for this scan...')

                if self.observatory.filter_wheel is not None and self.recenter_filters is not None:
                    if self.observatory.filters[self.observatory.filter_wheel.Position] not in self.recenter_filters:
                        logger.info('Current filter not in recenter filters, switching to the next filter...')

                        for i in range(self.observatory.filter_wheel.Position+1, len(self.observatory.filters)):
                            if self.observatory.filters[i] in self.recenter_filters:
                                self._hardware_status = None
                                t = threading.Thread(target=self._is_process_complete, 
                                    args=(self._hardware_status, self.hardware_timeout),
                                    daemon=True, name='is_filter_change_done_thread')
                                t.start()
                                self._hardware_status = self.observatory.set_filter_offset_focuser(filter_name=self.observatory.filters[i])
                                break
                        else:
                            for i in range(self.observatory.filter_wheel.Position-1):
                                if self.observatory.filters[i] in self.recenter_filters:
                                    self._hardware_status = None
                                    t = threading.Thread(target=self._is_process_complete,
                                        args=(self._hardware_status, self.hardware_timeout),
                                        daemon=True, name='is_filter_change_done_thread')
                                    t.start()
                                    self._hardware_status = self.observatory.set_filter_offset_focuser(filter_name=self.observatory.filters[i])
                                    break
                            else:
                                raise TelrunError('No filters in filter wheel are recenter filters')

                self.observatory.camera.ReadoutMode = self.default_readout
                
                if not slew: add_attempt = 1
                else: add_attempt = 0

                t = threading.Thread(target=self._is_process_complete,
                    args=(centered, self.hardware_timeout),
                    daemon=True, name='is_recenter_done_thread')
                t.start()
                centered = self.observatory.recenter(obj=source, 
                            target_x_pixel=scan.posx, target_y_pixel=scan.posy,
                            initial_offset_dec=self.recenter_initial_offset_dec,
                            check_and_refine=self.recenter_check_and_refine,
                            max_attempts=self.recenter_max_attempts+add_attempt,
                            tolerance=self.recenter_tolerance,
                            exposure=self.recenter_exposure,
                            save_images=self.recenter_save_images,
                            save_path=self.recenter_save_path,
                            sync_mount=self.recenter_sync_mount, 
                            do_initial_slew=slew)
                
                if not centered:
                    logger.warning('Recentering failed, continuing anyway...')
                else:
                    logger.info('Recentering succeeded, continuing...')
            # If not requested, just slew to the source
            elif slew:
                logger.info('Slewing to source...')

                self._hardware_status = None
                t = threading.Thread(target=self._is_process_complete,
                    args=(self._hardware_status, self.hardware_timeout),
                    daemon=True, name='is_slew_done_thread')
                self._hardware_status = self.observatory.slew_to_coordinates(obj=source, control_dome=(self.dome is not None), 
                control_rotator=(self.rotator is not None), wait_for_slew=False, track=False)
            
            # Set filter and focus offset
            if self.filter_wheel is not None:
                logger.info('Setting filter offset...')
                self._hardware_status = None
                t = threading.Thread(target=self._is_process_complete,
                    args=(self._hardware_status, self.hardware_timeout),
                    daemon=True, name='is_filter_change_done_thread')
                self._hardware_status = self.observatory.set_filter_offset_focuser(filter_name=scan.filter)

            # Set binning
            if scan.binx >= 1 and scan.binx <= self.observatory.camera.MaxBinX:
                logger.info('Setting binx to %i' % scan.binx)
                self.observatory.camera.BinX = scan.binx
            else:
                logger.warning('Requested binx of %i is not supported, skipping...' % scan.binx)
                self._set_scan_status(scan, 'F', message='Requested binx of %i is not supported' % scan.binx)
                continue

            if (scan.biny >= 1 and scan.biny <= self.observatory.camera.MaxBinY
                and (scan.CanAsymmetricBin or scan.biny == scan.binx)):
                logger.info('Setting biny to %i' % scan.biny)
                self.observatory.camera.BinY = scan.biny
            else:
                logger.warning('Requested biny of %i is not supported, skipping...' % scan.biny)
                self._set_scan_status(scan, 'F', message='Requested biny of %i is not supported' % scan.biny)
                continue

            # Set subframe
            if (scan.startx + scan.numx < 
                self.observatory.camera.CameraXSize/self.observatory.camera.BinX):
                logger.info('Setting startx and numx to %i, %i' % (scan.startx, scan.numx))
                self.observatory.camera.StartX = scan.startx
                self.observatory.camera.NumX = scan.numx
            else:
                logger.warning('Requested startx and numx of %i, %i is not supported, skipping...' % (
                    scan.startx, scan.numx))
                self._set_scan_status(scan, 'F', message='Requested startx and numx of %i, %i is not supported' % (
                    scan.startx, scan.numx))
                continue

            if (scan.starty + scan.numy <
                self.observatory.camera.CameraYSize/self.observatory.camera.BinY):
                logger.info('Setting starty and numy to %i, %i' % (scan.starty, scan.numy))
                self.observatory.camera.StartY = scan.starty
                self.observatory.camera.NumY = scan.numy
            else:
                logger.warning('Requested starty and numy of %i, %i is not supported, skipping...' % (
                    scan.starty, scan.numy))
                self._set_scan_status(scan, 'F', message='Requested starty and numy of %i, %i is not supported' % (
                    scan.starty, scan.numy))
                continue

            # Set readout mode
            try: 
                logger.info('Setting readout mode to %i' % scan.readout)
                self.observatory.camera.ReadoutMode = scan.readout
            except:
                logger.warning('Requested readout mode of %i is not supported, setting to default of %i' % (
                    scan.readout, self.default_readout))
                self.observatory.camera.ReadoutMode = self.default_readout
            
            # Wait for any motion to complete
            logger.info('Waiting for telescope motion to complete...')
            while self.observatory.telescope.Slewing:
                time.sleep(0.1)
            
            # Settle time
            logger.info('Waiting for settle time of %.1f seconds...' % self.observatory.settle_time)
            time.sleep(self.observatory.settle_time)

            # Start tracking
            logger.info('Starting tracking...')
            self.observatory.telescope.Tracking = True

            # Check for non-sidereal tracking
            if scan.pm_ra_cosdec != 0 or scan.pm_dec != 0:
                logger.info('Switching to non-sidereal tracking...')
                self.observatory.mount.RightAscensionRate = (
                    scan.pm_ra_cosdec * 0.997269567 / 15.041 
                    * (1/np.cos(np.deg2rad(scan.dec))))
                self.observatory.mount.DeclinationRate = scan.pm_dec
                logger.info('RA rate: %.2f arcsec/sec' % self.observatory.mount.RightAscensionRate)
                logger.info('Dec rate: %.2f arcsec/sec' % self.observatory.mount.DeclinationRate)

            # Derotation
            if self.observatory.rotator is not None:
                logger.info('Waiting for rotator motion to complete...')
                while self.observatory.rotator.IsMoving:
                    time.sleep(0.1)
                logger.info('Starting derotation...')
                self.observatory.start_derotation_thread()
            
            # Wait for focuser, dome motion to complete
            condition = True
            logger.info('Waiting for focuser or dome motion to complete...')
            while condition:
                if self.observatory.focuser is not None:
                    condition = self.observatory.focuser.IsMoving
                if self.observatory.dome is not None:
                    condition = condition or self.observatory.dome.Slewing
                time.sleep(0.1)
            
            # If still time before scan start, wait
            seconds_until_start_time = scan.start_time - time.time()
            if seconds_until_start_time > 0 and self.wait_for_scan_start_time:
                logging.info("Waiting %.1f seconds until start time" % seconds_until_start_time)
                time.sleep(seconds_until_start_time-0.1)
            
            # Start exposure
            logger.info('Starting %4.4g second exposure...' % scan.exposure)
            t0 = time.time()
            self.observatory.camera.Expose(scan.exposure, scan.light)
            logger.info('Waiting for image...')
            while not self.observatory.camera.ImageReady and time.time() < t0 + scan.exposure + self.hardware_timeout:
                time.sleep(0.1)
            
            custom_header = {'OBSNAME': scan.observer, 
                                'OBSCODE': scan.obscode,
                                'TARGET': scan.target_name, 
                                'CENTERED': centered,
                                'LASTAUTO': self.last_autofocus_time,
                                'BESTFOC': best_focus_result}

            # WCS thread cleanup
            self._wcs_thread = [t for t in self._wcs_thread if t.is_alive()]

            # Save image, do WCS if filter in wcs_filters
            if self.observatory.filter_wheel is not None:
                if self.observatory.filter_wheel.Position in self.wcs_filters:
                    save_success = self.observatory.save_last_image(self.telhome + '/images/' + 
                            scan.filename+'.tmp', frametyp=scan.light, custom_header=custom_header)
                    self._wcs_thread.append(threading.Thread(target=self._async_wcs_solver,
                                                args=(self.telhome + '/images/' + scan.filename+'.tmp',), 
                                                daemon=True, name='wcs_thread'))
                    self._wcs_thread[-1].start()
                else:
                    save_success = self.observatory.save_last_image(self.telhome + '/images/' + 
                            scan.filename, frametyp=scan.light, custom_header=custom_header)
                    logger.info('Current filter not in wcs filters, skipping WCS solve...')
            else:
                save_success = self.observatory.save_last_image(self.telhome + '/images/' + 
                            scan.filename+'.tmp', frametyp=scan.light, custom_header=custom_header)
                self._wcs_thread.append(threading.Thread(target=self._async_wcs_solver,
                                                args=(self.telhome + '/images/' + scan.filename+'.tmp',), 
                                                daemon=True, name='wcs_thread'))
                self._wcs_thread[-1].start()

            # Set scan status to done
            self._set_scan_status(scan, 'D')
        
        logger.info('Scan loop complete')
        self._skipped_scan_count = 0
        self._current_scan = None
        self._current_scan_index = None
        self._previous_scan = None
        self._previous_scan_index = None
        self._next_scan = None
        self._next_scan_index = None
        return True
    
    def _set_scan_status(self, scan, status, message=None):
        scan.status = status
        scan.status_message = message
        self._skipped_scan_count += 1

    def _async_wcs_solver(self, image_path):
        logger.info('Attempting a plate solution...')

        if type(self.observatory.wcs) not in (iter, list, tuple):
            logger.info('Using solver %s' % self.wcs_driver)
            solution = self.wcs.Solve(filename, ra_key='OBJCTRA', dec_key='OBJCTDEC', 
                ra_dec_units=('hour', 'deg'), solve_timeout=self.wcs_timeout, 
                scale_units='arcsecperpix', scale_type='ev',
                scale_est=self.observatory.pixel_scale[0], 
                scale_err=self.observatory.pixel_scale[0]*0.1,
                parity=1, crpix_center=True)
        else: 
            for wcs, i in enumerate(self.wcs):
                logger.info('Using solver %s' % self.wcs_driver[i])
                solution = wcs.Solve(filename, ra_key='OBJCTRA', dec_key='OBJCTDEC',
                    ra_dec_units=('hour', 'deg'), solve_timeout=self.wcs_timeout,
                    scale_units='arcsecperpix', scale_type='ev',
                    scale_est=self.observatory.pixel_scale[0], 
                    scale_err=self.observatory.pixel_scale[0]*0.1,
                    parity=1, crpix_center=True)
                if solution: break
        
        if not solution: logger.warning('WCS solution not found.')
        else: logger.info('WCS solution found.')

        logger.info('Removing tmp extension...')
        shutil.move(image_path, image_path.replace('.tmp', ''))
        logger.info('File %s complete' % image_path.replace('.tmp', ''))
    
    def _is_process_complete(self, check_var, timeout):
        t0 = time.time()
        while time.time() < t0 + timeout and check_var is None:
            pass
        else:
            raise TelrunError('Hardware timed out')
    
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
    def do_periodic_autofocus(self):
        return self._do_periodic_autofocus
    
    @property
    def last_autofocus_time(self):
        return self._last_autofocus_time

    @property
    def skipped_scan_count(self):
        return self._skipped_scan_count
    
    @property
    def current_scan(self):
        return self._current_scan

    @property
    def current_scan_index(self):
        return self._current_scan_index
    
    @property
    def previous_scan(self):
        return self._previous_scan
    
    @property
    def previous_scan_index(self):
        return self._previous_scan_index
    
    @property
    def next_scan(self):
        return self._next_scan
    
    @property
    def next_scan_index(self):
        return self._next_scan_index
    
    @property
    def initial_home(self):
        return self._initial_home
    @initial_home.setter
    def initial_home(self, value):
        self._initial_home = bool(value)
        self._config['initial_home'] = str(value)

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
    def _wait_for_cooldown(self):
        return self._wait_for_cooldown
    @_wait_for_cooldown.setter
    def _wait_for_cooldown(self, value):
        self._wait_for_cooldown = bool(value)
        self._config['wait_for_cooldown'] = str(value)

    @property
    def default_readout(self):
        return self._default_readout
    @default_readout.setter
    def default_readout(self, value):
        self._default_readout = int(value)
        self._config['default_readout'] = str(value)
    
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
    def autofocus_filters(self):
        return self._autofocus_filters
    @autofocus_filters.setter
    def autofocus_filters(self, value):
        self._autofocus_filters = value
        for v in value:
            self._config['autofocus_filters'] += (str(v) + ',')

    @property
    def autofocus_exposure(self):
        return self._autofocus_exposure
    @autofocus_exposure.setter
    def autofocus_exposure(self, value):
        self._autofocus_exposure = float(value)
        self._config['autofocus_exposure'] = str(value)
    
    @property
    def autofocus_midpoint(self):
        return self._autofocus_midpoint
    @autofocus_midpoint.setter
    def autofocus_midpoint(self, value):
        self._autofocus_midpoint = float(value)
        self._config['autofocus_midpoint'] = str(value)

    @property
    def autofocus_nsteps(self):
        return self._autofocus_nsteps
    @autofocus_nsteps.setter
    def autofocus_nsteps(self, value):
        self._autofocus_nsteps = int(value)
        self._config['autofocus_nsteps'] = str(value)
    
    @property
    def autofocus_step_size(self):
        return self._autofocus_step_size
    @autofocus_step_size.setter
    def autofocus_step_size(self, value):
        self._autofocus_step_size = int(value)
        self._config['autofocus_step_size'] = str(value)
    
    @property
    def autofocus_use_current_pointing(self):
        return self._autofocus_use_current_pointing
    @autofocus_use_current_pointing.setter
    def autofocus_use_current_pointing(self, value):
        self._autofocus_use_current_pointing = bool(value)
        self._config['autofocus_use_current_pointing'] = str(value)
    
    @property
    def autofocus_timeout(self):
        return self._autofocus_timeout
    @autofocus_timeout.setter
    def autofocus_timeout(self, value):
        self._autofocus_timeout = float(value)
        self._config['autofocus_timeout'] = str(value)

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
        if value < 0: 
            value = 1e99
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
    def recenter_filters(self):
        return self._recenter_filters
    @recenter_filters.setter
    def recenter_filters(self, value):
        self._recenter_filters = value
        for v in value:
            self._config['recenter_filters'] += (str(v) + ',')
    
    @property
    def recenter_initial_offset_dec(self):
        return self._recenter_initial_offset_dec
    @recenter_initial_offset_dec.setter
    def recenter_initial_offset_dec(self, value):
        self._recenter_initial_offset_dec = float(value)
        self._config['recenter_initial_offset_dec'] = str(value)
    
    @property
    def recenter_check_and_refine(self):
        return self._recenter_check_and_refine
    @recenter_check_and_refine.setter
    def recenter_check_and_refine(self, value):
        self._recenter_check_and_refine = bool(value)
        self._config['recenter_check_and_refine'] = str(value)
    
    @property
    def recenter_max_attempts(self):
        return self._recenter_max_attempts
    @recenter_max_attempts.setter
    def recenter_max_attempts(self, value):
        self._recenter_max_attempts = int(value)
        self._config['recenter_max_attempts'] = str(value)

    @property
    def recenter_tolerance(self):
        return self._recenter_tolerance
    @recenter_tolerance.setter
    def recenter_tolerance(self, value):
        self._recenter_tolerance = float(value)
        self._config['recenter_tolerance'] = str(value)

    @property
    def recenter_exposure(self):
        return self._recenter_exposure
    @recenter_exposure.setter
    def recenter_exposure(self, value):
        self._recenter_exposure = float(value)
        self._config['recenter_exposure'] = str(value)
    
    @property
    def recenter_save_images(self):
        return self._recenter_save_images
    @recenter_save_images.setter
    def recenter_save_images(self, value):
        self._recenter_save_images = bool(value)
        self._config['recenter_save_images'] = str(value)

    @property
    def recenter_save_path(self):
        return self._recenter_save_path
    @recenter_save_path.setter
    def recenter_save_path(self, value):
        self._recenter_save_path = value
        self._config['recenter_save_path'] = str(value)
    
    @property
    def recenter_sync_mount(self):
        return self._recenter_sync_mount
    @recenter_sync_mount.setter
    def recenter_sync_mount(self, value):
        self._recenter_sync_mount = bool(value)
        self._config['recenter_sync_mount'] = str(value)

    @property
    def hardware_timeout(self):
        return self._hardware_timeout
    @hardware_timeout.setter
    def hardware_timeout(self, value):
        self._hardware_timeout = float(value)
        self._config['hardware_timeout'] = str(value)
    
    @property
    def wcs_filters(self):
        return self._wcs_filters
    @wcs_filters.setter
    def wcs_filters(self, value):
        self._wcs_filters = value
        for v in value:
            self._config['wcs_filters'] += (str(v) + ',')

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

def setup_telrun_observatory(telhome):
    pass