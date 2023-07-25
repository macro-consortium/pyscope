import atexit
import configparser
import logging
import os
import shutil
import threading
import tkinter as tk
import tkinter.ttk as ttk

from astropy import coordinates as coord, time as astrotime, units as u

from pyscope import Observatory

logger = logging.getLogger(__name__)

_gui_font = tk.font.Font(family='Segoe UI', size=10)

class TelrunOperator:
    def __init__(self, config_file_path=None, gui=False, **kwargs):

        # Non-accessible variables
        self._config = configparser.ConfigParser()
        self._gui = None
        self._telrun_file = None
        self._best_focus_result = None
        self._hardware_status = None
        self._wcs_thread = []

        # Read-only variables without kwarg setters
        self._do_periodic_autofocus = True
        self._last_autofocus_time = None
        self._skipped_scan_count = 0
        self._current_scan = None
        self._current_scan_index = None
        self._previous_scan = None
        self._previous_scan_index = None
        self._next_scan = None
        self._next_scan_index = None
        self._autofocus_status = None
        self._camera_status = None
        self._cover_calibrator_status = None
        self._dome_status = None
        self._filter_wheel_status = None
        self._focuser_status = None
        self._observing_conditions_status = None
        self._rotator_status = None
        self._safety_monitor_status = None
        self._switch_status = None
        self._telescope_status = None
        self._wcs_status = None

        # Read-only variables with kwarg setters
        self._telhome = None
        self._observatory = None
        self._dome_type = None # None, 'dome' or 'safety-monitor' or 'both'

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
            self._initial_home = self._config.getboolean('initial_home')
            self._wait_for_sun = self._config.getboolean('wait_for_sun')
            self._max_solar_elev = self._config.getfloat('max_solar_elev')
            self._check_safety_monitors = self._config.getboolean('check_safety_monitors')
            self._wait_for_cooldown = self._config.getboolean('wait_for_cooldown')
            self._default_readout = self._config.getint('default_readout')
            self._autofocus_interval = self._config.getfloat('autofocus_interval')
            self._initial_autofocus = self._config.getboolean('initial_autofocus')
            self._autofocus_filters = [f.strip() for f in self._config.get('autofocus_filters').split(',')]
            self._autofocus_exposure = self._config.getfloat('autofocus_exposure')
            self._autofocus_midpoint = self._config.getfloat('autofocus_midpoint')
            self._autofocus_nsteps = self._config.getint('autofocus_nsteps')
            self._autofocus_step_size = self._config.getfloat('autofocus_step_size')
            self._autofocus_use_current_pointing = self._config.getboolean('autofocus_use_current_pointing')
            self._autofocus_timeout = self._config.getfloat('autofocus_timeout')
            self._wait_for_scan_start_time = self._config.getboolean('wait_for_scan_start_time')
            self._max_scan_late_time = self._config.getfloat('max_scan_late_time')
            self._preslew_time = self._config.getfloat('preslew_time')
            self._recenter_filters = [f.strip() for f in self._config.get('recenter_filters').split(',')]
            self._recenter_initial_offset_dec = self._config.getfloat('recenter_initial_offset_dec')
            self._recenter_check_and_refine = self._config.getboolean('recenter_check_and_refine')
            self._recenter_max_attempts = self._config.getint('recenter_max_attempts')
            self._recenter_tolerance = self._config.getfloat('recenter_tolerance')
            self._recenter_exposure = self._config.getfloat('recenter_exposure')
            self._recenter_save_images = self._config.getboolean('recenter_save_images')
            self._recenter_save_path = self._config.get('recenter_save_path')
            self._recenter_sync_mount = self._config.getboolean('recenter_sync_mount')
            self._hardware_timeout = self._config.getfloat('hardware_timeout')
            self._wcs_filters = [f.strip() for f in self._config.get('wcs_filters').split(',')]
            self._wcs_timeout = self._config.getfloat('wcs_timeout')
        
        # Load kwargs
        
        # Parse telhome
        self._telhome = kwargs.get('telhome', self._telhome)
        if self._telhome is None:
            self._telhome = os.path.abspath(os.getcwd())
        setup_telrun_observatory(self._telhome)
        self._config['telhome'] = str(self._telhome)

        # Parse observatory
        self._observatory = kwargs.get('observatory', self._observatory)
        if self._observatory is None:
            raise TelrunError('observatory must be specified')
        elif type(self._observatory) is str:
            self._config['observatory'] = self._observatory
            self._observatory = Observatory(config_file_path=self._observatory)
        elif type(self._observatory) is Observatory:
            self._config['observatory'] = str(self.telhome + '/config/observatory.cfg')
            self.observatory.save_config(self._config['observatory'])
        else:
            raise TelrunError('observatory must be a string representing a config file path \
                or an Observatory object')

        # Parse dome_type
        self._dome_type = kwargs.get('dome_type', self._dome_type)
        match self._dome_type:
            case None | 'None' | 'none':
                self._dome_type = 'None'
            case 'dome' | 'safety-monitor' | 'safety_monitor' | 'safetymonitor' | 'safety monitor' | 'both':
                pass
            case _:
                raise TelrunError('dome_type must be None, "dome", "safety-monitor", "both", or "None"')
        self._config['dome_type'] = str(self._dome_type)

        # Parse other kwargs
        self.initial_home = kwargs.get('initial_home', self._initial_home)
        self.wait_for_sun = kwargs.get('wait_for_sun', self._wait_for_sun)
        self.max_solar_elev = kwargs.get('max_solar_elev', self._max_solar_elev)
        self.check_safety_monitors = kwargs.get('check_safety_monitors', self._check_safety_monitors)
        self.wait_for_cooldown = kwargs.get('wait_for_cooldown', self._wait_for_cooldown)
        self.default_readout = kwargs.get('default_readout', self._default_readout)
        self.autofocus_interval = kwargs.get('autofocus_interval', self._autofocus_interval)
        self.initial_autofocus = kwargs.get('initial_autofocus', self._initial_autofocus)
        self.autofocus_filters = kwargs.get('autofocus_filters', self._autofocus_filters)
        self.autofocus_exposure = kwargs.get('autofocus_exposure', self._autofocus_exposure)
        self.autofocus_midpoint = kwargs.get('autofocus_midpoint', self._autofocus_midpoint)
        self.autofocus_nsteps = kwargs.get('autofocus_nsteps', self._autofocus_nsteps)
        self.autofocus_step_size = kwargs.get('autofocus_step_size', self._autofocus_step_size)
        self.autofocus_use_current_pointing = kwargs.get('autofocus_use_current_pointing', self._autofocus_use_current_pointing)
        self.autofocus_timeout = kwargs.get('autofocus_timeout', self._autofocus_timeout)
        self.wait_for_scan_start_time = kwargs.get('wait_for_scan_start_time', self._wait_for_scan_start_time)
        self.max_scan_late_time = kwargs.get('max_scan_late_time', self._max_scan_late_time)
        self.preslew_time = kwargs.get('preslew_time', self._preslew_time)
        self.recenter_filters = kwargs.get('recenter_filters', self._recenter_filters)
        self.recenter_initial_offset_dec = kwargs.get('recenter_initial_offset_dec', self._recenter_initial_offset_dec)
        self.recenter_check_and_refine = kwargs.get('recenter_check_and_refine', self._recenter_check_and_refine)
        self.recenter_max_attempts = kwargs.get('recenter_max_attempts', self._recenter_max_attempts)
        self.recenter_tolerance = kwargs.get('recenter_tolerance', self._recenter_tolerance)
        self.recenter_exposure = kwargs.get('recenter_exposure', self._recenter_exposure)
        self.recenter_save_images = kwargs.get('recenter_save_images', self._recenter_save_images)
        self.recenter_save_path = kwargs.get('recenter_save_path', self._recenter_save_path)
        self.recenter_sync_mount = kwargs.get('recenter_sync_mount', self._recenter_sync_mount)
        self.hardware_timeout = kwargs.get('hardware_timeout', self._hardware_timeout)
        self.wcs_filters = kwargs.get('wcs_filters', self._wcs_filters)
        self.wcs_timeout = kwargs.get('wcs_timeout', self._wcs_timeout)

        # Set filters up if None
        if self.autofocus_filters is None:
            self.autofocus_filters = self.observatory.filters
        if self.recenter_filters is None:
            self.recenter_filters = self.observatory.filters
        if self.wcs_filters is None:
            self.wcs_filters = self.observatory.filters
        
        # Register shutdown with atexit
        logger.debug('Registering observatory shutdown with atexit')
        atexit.register(self._terminate())
        logger.debug('Registered')

        # Open GUI if requested
        if self._gui:
            logger.info('Starting GUI')
            root = tk.Tk()
            root.tk.call('source', '../src/themeSetup.tcl')
            root.tk.call('set_theme', 'dark')
            # icon_photo = tk.PhotoImage(file='images/UILogo.png')
            # root.iconphoto(False, icon_photo)
            self._gui = TelrunGUI(root)
            self._gui.mainloop()
            logger.info('GUI started')

        # Connect to observatory hardware
        logger.info('Attempting to connect to observatory hardware')
        self.observatory.connect_all()
        logger.info('Connected')
        self._autofocus_status = 'Idle'
        self._camera_status = 'Idle'
        if self.observatory.cover_calibrator is not None:
            self._cover_calibrator_status = 'Idle'
        if self.observatory.dome is not None:
            self._dome_status = 'Idle'
        if self.observatory.filter_wheel is not None:
            self._filter_wheel_status = 'Idle'
        if self.observatory.focuser is not None:
            self._focuser_status = 'Idle'
        if self.observatory.observing_conditions is not None:
            self._observing_conditions_status = 'Idle'
        if self.observatory.rotator is not None:
            self._rotator_status = 'Idle'
        if self.observatory.safety_monitor is not None:
            self._safety_monitor_status = 'Idle'
        if self.observatory.switch is not None:
            self._switch_status = 'Idle'
        self._telescope_status = 'Idle'
        if self.observatory.wcs is not None:
            self._wcs_status = 'Idle'
    
    def save_config(self, filename):
        save_dir = self.telhome + '/config/'
        self.observatory.save_config(save_dir+'observatory.cfg')
        self._config['observatory'] = save_dir+'observatory.cfg'
        with open(save_dir + filename, 'w') as config_file:
            self._config.write(config_file)

    def start(self):
        logger.info('Checking for an existing telrun.sls file')
        if os.path.isfile(self.telhome + '/schedules/telrun.sls'):
            logger.info('Loading existing telrun.sls')
            self._telrun_file = TelrunFile(self.telhome + '/schedules/telrun.sls')

        if self.observatory.observing_conditions is not None:
            logger.info('Starting the observing_conditions update thread...')
            self._observing_conditions_status = 'Update thread running'
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
            self._telescope_status = 'Homing'
            self.observatory.telescope.FindHome()
            self._telescope_status = 'Idle'
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
                        self._dome_status = 'Opening shutter'
                        self.observatory.dome.OpenShutter()
                        self._dome_status = 'Idle'
                        logger.info('Opened.')
                    if self.observatory.dome.CanFindHome:
                        self._dome_status = 'Homing'
                        logger.info('Finding the dome home...')
                        self.observatory.dome.FindHome()
                        self._dome_status = 'Idle'
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
                        self._dome_status = 'Opening shutter'
                        self.observatory.dome.OpenShutter()
                        self._dome_status = 'Idle'
                        logger.info('Opened.')
                    if self.observatory.dome.CanFindHome:
                        logger.info('Finding the dome home...')
                        self._dome_status = 'Homing'
                        self.observatory.dome.FindHome()
                        self._dome_status = 'Idle'
                        logger.info('Found.')
        
        # Wait for cooler?
        while (self.observatory.camera.CCDTemperature > 
                self.observatory.cooler_setpoint + self.observatory.cooler_tolerance
                and self.wait_for_cooldown):
            logger.info('CCD temperature: %.3f degs (above limit of %.3f with %.3f tolerance)' % (
                self.observatory.camera.CCDTemperature,
                self.observatory.cooler_setpoint, 
                self.observatory.cooler_tolerance))
            self._camera_status = 'Cooling'
            time.sleep(10)
        logger.info('CCD temperature: %.3f degs (below limit of %.3f with %.3f tolerance), continuing...' % (
            self.observatory.camera.CCDTemperature,
            self.observatory.cooler_setpoint,
            self.observatory.cooler_tolerance))
        self._camera_status = 'Idle'

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
                self._set_scan_status(scan_index, 'F', message='Scan already attempted to be processed')
                continue
        
            # Check 2: Wait for scan start time?
            if scan.start_time is None:
                logger.info('No scan start time, starting now...')
                scan.start_time = astrotime.Time.now()

            seconds_until_start_time = (scan.start_time - astrotime.Time.now()).sec
            if not self.wait_for_scan_start_time and seconds_until_start_time < self.max_scan_late_time:
                logger.info('Ignoring scan start time, continuing...')
            elif not self.wait_for_scan_start_time and seconds_until_start_time > self.max_scan_late_time:
                logger.info('Ignoring scan start time, however \
                    scan start time exceeded max_scan_late_time of %i seconds, skipping...' % self.max_scan_late_time)
                self._set_scan_status(scan_index, 'F', message='Exceeded max_scan_late_time')
                continue
            elif self.wait_for_scan_start_time and seconds_until_start_time > self.max_scan_late_time:
                logger.info('Scan start time exceeded max_scan_late_time of %i seconds, skipping...' % self.max_scan_late_time)
                self._set_scan_status(scan_index, 'F', message='Exceeded max_scan_late_time')
                continue
            else:
                logger.info('Waiting %.1f seconds (%.2f hours) for scan start time...' % (
                    seconds_until_start_time, seconds_until_start_time/3600))
            
            while self.wait_for_scan_start_time and seconds_until_start_time > self.preslew_time:
                time.sleep(0.1)
                seconds_until_start_time = (scan.start_time - astrotime.Time.now()).sec
            else:
                if seconds_until_start_time > 0:
                    logger.info('Scan start time in %.1f seconds' % seconds_until_start_time)
            
            # Check 3: Dome status?
            match self.dome_type:
                case 'dome':
                    if self.observatory.dome is not None and self.observatory.dome.CanSetShutter:
                        if self.observatory.dome.ShutterStatus != 0:
                            logger.info('Dome shutter is not open, skipping...')
                            self._set_scan_status(scan_index, 'F', message='Dome shutter is not open')
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
                            self._set_scan_status(scan_index, 'F', message='Dome safety monitor indicates unsafe')
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
                            self._set_scan_status(scan_index, 'F', message='Dome safety monitor indicates unsafe')
                            continue
                    
                    if self.observatory.dome is not None and self.observatory.dome.CanSetShutter:
                        if self.observatory.dome.ShutterStatus != 0:
                            logger.info('Dome shutter is not open, skipping...')
                            self._set_scan_status(scan_index, 'F', message='Dome shutter is not open')
                            continue
            
            # Check 4: Check safety monitors?
            if self.check_safety_monitors:
                logger.info('Checking safety monitor statuses')

                status = True
                if type(self.observatory.safety_monitor) not in (iter, list, tuple):
                    status = self.observatory.safety_monitor.IsSafe
                else:
                    for monitor in self.observatory.safety_monitor:
                        status = status and monitor.IsSafe
                
                if not status:
                    logger.info('Safety monitor indicates unsafe, skipping...')
                    self._set_scan_status(scan_index, 'F', message='Safety monitor indicates unsafe')
                    continue
            
            # Check 5: Wait for sun?
            sun_alt_degs = self.observatory.sun_altaz()[0]
            if self.wait_for_sun and sun_alt_degs > self.max_solar_elev:
                logger.info('Sun altitude: %.3f degs (above limit of %s), skipping...' % (
                    sun_alt_degs, self.max_solar_elev))
                self._set_scan_status(scan_index, 'F', message='Sun altitude above limit')
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
                                self._filter_wheel_status = 'Changing filter'
                                self._focuser_status = 'Offsetting for filter selection' if self.observatory.focuser is not None else None
                                self.observatory.set_filter_offset_focuser(filter_name=self.observatory.filters[i])
                                self._filter_wheel_status = 'Idle'
                                self._focuser_status = 'Idle' if self.observatory.focuser is not None else None
                                break
                        else:
                            for i in range(self.observatory.filter_wheel.Position-1):
                                if self.observatory.filters[i] in self.autofocus_filters:
                                    self._filter_wheel_status = 'Changing filter'
                                    self._focuser_status = 'Offsetting for filter selection' if self.observatory.focuser is not None else None
                                    self.observatory.set_filter_offset_focuser(filter_name=self.observatory.filters[i])
                                    self._filter_wheel_status = 'Idle'
                                    self._focuser_status = 'Idle' if self.observatory.focuser is not None else None
                                    break
                            else:
                                raise TelrunError('No filters in filter wheel are autofocus filters')

                self.observatory.camera.ReadoutMode = self.default_readout

                t = threading.Thread(target=self._is_process_complete, 
                    args=(self._best_focus_result, self.autofocus_timeout),
                    daemon=True, name='is_autofocus_done_thread')
                t.start()

                self._autofocus_status = 'Running'
                self._best_focus_result = self.observatory.run_autofocus(
                    exposure=self.autofocus_exposure,
                    midpoint=self.autofocus_midpoint,
                    nsteps=self.autofocus_nsteps,
                    step_size=self.autofocus_step_size,
                    use_current_pointing=self.autofocus_use_current_pointing)
                self._autofocus_status = 'Idle'
                
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
                self._camera_status = 'Cooling'
            logger.info('CCD temperature: %.3f degs (below limit of %.3f with %.3f tolerance), continuing...' % (
                self.observatory.camera.CCDTemperature,
                self.observatory.cooler_setpoint,
                self.observatory.cooler_tolerance))
            self._camera_status = 'Idle'
            
            # Is the previous target different?
            slew = True
            if self.previous_scan is not None:
                if (self.previous_scan.skycoord.ra.hourangle == scan.skycoord.ra.hourangle 
                        and self.previous_scan.skycoord.dec.deg == scan.skycoord.dec.deg
                        and self.previous_scan.status == 'D'
                        and best_focus_result is not None):
                    logger.info('Previous target is same ra and dec, skipping initial slew...')
                    slew = False
            
            # Perform centering if requested
            centered = None
            if None not in (scan.posx, scan.posy, scan.skycoord):
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
                                self._filter_wheel_status = 'Changing filter'
                                self._focuser_status = 'Offsetting for filter selection' if self.observatory.focuser is not None else None
                                self._hardware_status = self.observatory.set_filter_offset_focuser(filter_name=self.observatory.filters[i])
                                self._filter_wheel_status = 'Idle'
                                self._focuser_status = 'Idle' if self.observatory.focuser is not None else None
                                break
                        else:
                            for i in range(self.observatory.filter_wheel.Position-1):
                                if self.observatory.filters[i] in self.recenter_filters:
                                    self._hardware_status = None
                                    t = threading.Thread(target=self._is_process_complete,
                                        args=(self._hardware_status, self.hardware_timeout),
                                        daemon=True, name='is_filter_change_done_thread')
                                    t.start()
                                    self._filter_wheel_status = 'Changing filter'
                                    self._focuser_status = 'Offsetting for filter selection' if self.observatory.focuser is not None else None
                                    self._hardware_status = self.observatory.set_filter_offset_focuser(filter_name=self.observatory.filters[i])
                                    self._filter_wheel_status = 'Idle'
                                    self._focuser_status = 'Idle' if self.observatory.focuser is not None else None
                                    break
                            else:
                                raise TelrunError('No filters in filter wheel are recenter filters')

                self.observatory.camera.ReadoutMode = self.default_readout
                
                if not slew: add_attempt = 1
                else: add_attempt = 0

                self._hardware_status = None
                t = threading.Thread(target=self._is_process_complete,
                    args=(self._hardware_status, self.hardware_timeout),
                    daemon=True, name='is_recenter_done_thread')
                t.start()
                self._camera_status = 'Recentering'
                self._telescope_status = 'Recentering'
                self._wcs_status = 'Recentering' if self.observatory.wcs is not None else None
                self._dome_status = 'Recentering' if self.observatory.dome is not None else None
                self._rotator_status = 'Recentering' if self.observatory.rotator is not None else None
                self._hardware_status = self.observatory.recenter(obj=scan.skycoord, 
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
                centered = self._hardware_status
                self._camera_status = 'Idle'
                self._telescope_status = 'Idle'
                self._wcs_status = 'Idle' if self.observatory.wcs is not None else None
                self._dome_status = 'Idle' if self.observatory.dome is not None else None
                self._rotator_status = 'Idle' if self.observatory.rotator is not None else None

                if not centered:
                    logger.warning('Recentering failed, continuing anyway...')
                else:
                    logger.info('Recentering succeeded, continuing...')
            # If not requested, just slew to the source
            elif slew and scan.skycoord is not None:
                logger.info('Slewing to source...')

                self._hardware_status = None
                t = threading.Thread(target=self._is_process_complete,
                    args=(self._hardware_status, self.hardware_timeout),
                    daemon=True, name='is_slew_done_thread')
                t.start()
                self._telescope_status = 'Slewing'
                self._dome_status = 'Slewing' if self.observatory.dome is not None else None
                self._rotator_status = 'Slewing' if self.observatory.rotator is not None else None
                self._hardware_status = self.observatory.slew_to_coordinates(obj=scan.skycoord, control_dome=(self.dome is not None), 
                control_rotator=(self.rotator is not None), wait_for_slew=False, track=False)
            
            # Set filter and focus offset
            if self.filter_wheel is not None:
                logger.info('Setting filter offset...')
                self._hardware_status = None
                t = threading.Thread(target=self._is_process_complete,
                    args=(self._hardware_status, self.hardware_timeout),
                    daemon=True, name='is_filter_change_done_thread')
                t.start()
                self._filter_wheel_status = 'Changing filter'
                self._focuser_status = 'Offsetting for filter selection' if self.observatory.focuser is not None else None
                self._hardware_status = self.observatory.set_filter_offset_focuser(filter_name=scan.filter)
                self._filter_wheel_status = 'Idle'

            # Set binning
            if scan.binx >= 1 and scan.binx <= self.observatory.camera.MaxBinX:
                logger.info('Setting binx to %i' % scan.binx)
                self.observatory.camera.BinX = scan.binx
            else:
                logger.warning('Requested binx of %i is not supported, skipping...' % scan.binx)
                self._set_scan_status(scan_index, 'F', message='Requested binx of %i is not supported' % scan.binx)
                continue

            if (scan.biny >= 1 and scan.biny <= self.observatory.camera.MaxBinY
                and (scan.CanAsymmetricBin or scan.biny == scan.binx)):
                logger.info('Setting biny to %i' % scan.biny)
                self.observatory.camera.BinY = scan.biny
            else:
                logger.warning('Requested biny of %i is not supported, skipping...' % scan.biny)
                self._set_scan_status(scan_index, 'F', message='Requested biny of %i is not supported' % scan.biny)
                continue

            # Set subframe
            if scan.numx == 0: 
                scan.numx = self.observatory.camera.CameraXSize/self.observatory.camera.BinX
            if scan.numy == 0: 
                scan.numy = self.observatory.camera.CameraYSize/self.observatory.camera.BinY

            if (scan.startx + scan.numx < 
                self.observatory.camera.CameraXSize/self.observatory.camera.BinX):
                logger.info('Setting startx and numx to %i, %i' % (scan.startx, scan.numx))
                self.observatory.camera.StartX = scan.startx
                self.observatory.camera.NumX = scan.numx
            else:
                logger.warning('Requested startx and numx of %i, %i is not supported, skipping...' % (
                    scan.startx, scan.numx))
                self._set_scan_status(scan_index, 'F', message='Requested startx and numx of %i, %i is not supported' % (
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
                self._set_scan_status(scan_index, 'F', message='Requested starty and numy of %i, %i is not supported' % (
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
            self._telescope_status = 'Settling'
            time.sleep(self.observatory.settle_time)

            # Start tracking
            logger.info('Starting tracking...')
            self._telescope_status = 'Tracking'
            self.observatory.telescope.Tracking = True

            # Check for pm exceeding two pixels in one hour
            if (scan.skycoord.pm_ra_cosdec.to_value(u.arcsec/u.second) > 2*self.observatory.pixel_scale[0]/(60*60)
                or scan.skycoord.pm_dec.to_value(u.arcsec/u.second) > 2*self.observatory.pixel_scale[1]/(60*60)):
                logger.info('Switching to non-sidereal tracking...')
                self._telescope_status = 'Non-sidereal tracking'
                self.observatory.mount.RightAscensionRate = (
                    scan.skycoord.pm_ra_cosdec.to_value(u.arcsec/u.second)
                    * 0.997269567 / 15.041 
                    * (1/np.cos(np.deg2rad(scan.skycoord.dec.deg))))
                self.observatory.mount.DeclinationRate = scan.skycoord.pm_dec.to_value(u.arcsec/u.second)
                logger.info('RA rate: %.2f sec-angle/sec' % self.observatory.mount.RightAscensionRate)
                logger.info('Dec rate: %.2f arcsec/sec' % self.observatory.mount.DeclinationRate)

            # Derotation
            if self.observatory.rotator is not None:
                logger.info('Waiting for rotator motion to complete...')
                while self.observatory.rotator.IsMoving:
                    time.sleep(0.1)
                logger.info('Starting derotation...')
                self._rotator_status = 'Derotating'
                self.observatory.start_derotation_thread()
            
            # Wait for focuser, dome motion to complete
            condition = True
            logger.info('Waiting for focuser or dome motion to complete...')
            while condition:
                if self.observatory.focuser is not None:
                    condition = self.observatory.focuser.IsMoving
                    if not condition: self._focuser_status = 'Idle'
                if self.observatory.dome is not None:
                    if not self.observatory.Slewing: 
                        self._dome_status = 'Idle'
                    condition = condition or self.observatory.dome.Slewing
                time.sleep(0.1)
            
            # If still time before scan start, wait
            seconds_until_start_time = (scan.start_time - astrotime.Time.now()).sec
            if seconds_until_start_time > 0 and self.wait_for_scan_start_time:
                logging.info("Waiting %.1f seconds until start time" % seconds_until_start_time)
                time.sleep(seconds_until_start_time-0.1)
            
            # Start exposure
            logger.info('Starting %4.4g second exposure...' % scan.exposure)
            self._camera_status = 'Exposing'
            t0 = time.time()
            self.observatory.camera.Expose(scan.exposure, scan.light)
            logger.info('Waiting for image...')
            while not self.observatory.camera.ImageReady and time.time() < t0 + scan.exposure + self.hardware_timeout:
                time.sleep(0.1)
            self._camera_status = 'Idle'
            
            custom_header = {'OBSNAME': (scan.observer, 'Name of observer'), 
                                'OBSCODE': (scan.obscode, 'Observing code'),
                                'TARGET': (scan.target_name, 'Name of target if provided'),
                                'SCHEDTIT': (scan.title, 'Title if provided'),
                                'SCHEDCOM': (scan.comment, 'Comment if provided'),
                                'SCHEDRA': (scan.skycoord.ra.to_string(), 'Requested RA'),
                                'SCHEDDEC': (scan.skycoord.dec.to_string(), 'Requested Dec'),
                                'SCHEDPRA': (scan.skycoord.pm_ra_cosdec.to_value(u.arsec/u.hour), 'Requested proper motion in RAcosDec [arcsec/hr]'),
                                'SCHEDPDEC': (scan.skycoord.pm_dec.to_value(u.arcsec/u.hour), 'Requested proper motion in Dec [arcsec/hr]'),
                                'SCHEDSRT': (scan.start_time.fits, 'Requested start time'),
                                'SCHEDINT': (scan.interrupt_allowed, 'Whether the scan can be interrupted by autofocus'),
                                'CENTERED': (centered, 'Whether the target underwent the centering routine'),
                                'SCHEDPSX': (scan.posx, 'Requested x pixel for recentering'),
                                'SCHEDPSY': (scan.posy, 'Requested y pixel for recentering'),
                                'LASTAUTO': (self.last_autofocus_time, 'When the last autofocus was performed')}

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
            self._set_scan_status(scan_index, 'D')
        
        logger.info('Scan loop complete')
        self._skipped_scan_count = 0
        self._current_scan = None
        self._current_scan_index = None
        self._previous_scan = None
        self._previous_scan_index = None
        self._next_scan = None
        self._next_scan_index = None

        logger.info('Generating summary report')
        summary_report(self.telhome+'/schedules/telrun.sls', self.telhome+'/logs/'+
            self._telrun_file.scans[0].start_time.datetime.strftime('%m-%d-%Y')+'_telrun-report.txt')

        return True
    
    def _set_scan_status(self, scan_index, status, message=None):
        self._telrun_file.scans[scan_index].status = status
        self._telrun_file.scans[scan_index].end_time = astrotime.Time.now()

        if status == 'F':
            self._skipped_scan_count += 1

        self._telrun_file.update_status_code(scan_index, status, message)

    def _async_wcs_solver(self, image_path):
        logger.info('Attempting a plate solution...')
        self._wcs_status = 'Solving'

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
        self._wcs_status = 'Idle'
    
    def _is_process_complete(self, check_var, timeout):
        t0 = time.time()
        while time.time() < t0 + timeout and check_var is None:
            pass
        else:
            raise TelrunError('Hardware timed out')
    
    def _terminate(self):
        self.observatory.shutdown()
    
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
    def autofocus_status(self):
        return self._autofocus_status
    
    @property
    def camera_status(self):
        return self._camera_status
    
    @property
    def cover_calibrator_status(self):
        return self._cover_calibrator_status

    @property
    def dome_status(self):
        return self._dome_status
    
    @property
    def filter_wheel_status(self):
        return self._filter_wheel_status
    
    @property
    def focuser_status(self):
        return self._focuser_status
    
    @property
    def observing_conditions_status(self):
        return self._observing_conditions_status
    
    @property
    def rotator_status(self):
        return self._rotator_status
    
    @property
    def safety_monitor_status(self):
        return self._safety_monitor_status
    
    @property
    def switch_status(self):
        return self._switch_status
    
    @property
    def telescope_status(self):
        return self._telescope_status
    
    @property
    def wcs_status(self):
        return self._wcs_status
    
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
    def initial_home(self):
        return self._initial_home
    @initial_home.setter
    def initial_home(self, value):
        self._initial_home = bool(value)
        self._config['initial_home'] = str(self._initial_home)

    @property
    def wait_for_sun(self):
        return self._wait_for_sun
    @wait_for_sun.setter
    def wait_for_sun(self, value):
        self._wait_for_sun = bool(value)
        self._config['wait_for_sun'] = str(self._wait_for_sun)

    @property
    def max_solar_elev(self):
        return self._max_solar_elev
    @max_solar_elev.setter
    def max_solar_elev(self, value):
        self._max_solar_elev = float(value)
        self._config['max_solar_elev'] = str(self._max_solar_elev)
    
    @property
    def check_safety_monitors(self):
        return self._check_safety_monitors
    @check_safety_monitors.setter
    def check_safety_monitors(self, value):
        self._check_safety_monitors = bool(value)
        self._config['check_safety_monitors'] = str(self._check_safety_monitors)
    
    @property
    def _wait_for_cooldown(self):
        return self._wait_for_cooldown
    @_wait_for_cooldown.setter
    def _wait_for_cooldown(self, value):
        self._wait_for_cooldown = bool(value)
        self._config['wait_for_cooldown'] = str(self._wait_for_cooldown)

    @property
    def default_readout(self):
        return self._default_readout
    @default_readout.setter
    def default_readout(self, value):
        self._default_readout = int(value)
        self._config['default_readout'] = str(self._default_readout)
    
    @property
    def autofocus_interval(self):
        return self._autofocus_interval
    @autofocus_interval.setter
    def autofocus_interval(self, value):
        self._autofocus_interval = float(value)
        self._config['autofocus_interval'] = str(self._autofocus_interval)

    @property
    def initial_autofocus(self):
        return self._initial_autofocus
    @initial_autofocus.setter
    def initial_autofocus(self, value):
        self._initial_autofocus = bool(value)
        self._config['initial_autofocus'] = str(self._initial_autofocus)

    @property
    def autofocus_filters(self):
        return self._autofocus_filters
    @autofocus_filters.setter
    def autofocus_filters(self, value):
        self._autofocus_filters = iter(value)
        for v in value:
            self._config['autofocus_filters'] += (str(v) + ',')

    @property
    def autofocus_exposure(self):
        return self._autofocus_exposure
    @autofocus_exposure.setter
    def autofocus_exposure(self, value):
        self._autofocus_exposure = float(value)
        self._config['autofocus_exposure'] = str(self._autofocus_exposure)
    
    @property
    def autofocus_midpoint(self):
        return self._autofocus_midpoint
    @autofocus_midpoint.setter
    def autofocus_midpoint(self, value):
        self._autofocus_midpoint = float(value)
        self._config['autofocus_midpoint'] = str(self._autofocus_midpoint)

    @property
    def autofocus_nsteps(self):
        return self._autofocus_nsteps
    @autofocus_nsteps.setter
    def autofocus_nsteps(self, value):
        self._autofocus_nsteps = int(value)
        self._config['autofocus_nsteps'] = str(self._autofocus_nsteps)
    
    @property
    def autofocus_step_size(self):
        return self._autofocus_step_size
    @autofocus_step_size.setter
    def autofocus_step_size(self, value):
        self._autofocus_step_size = int(value)
        self._config['autofocus_step_size'] = str(self._autofocus_step_size)
    
    @property
    def autofocus_use_current_pointing(self):
        return self._autofocus_use_current_pointing
    @autofocus_use_current_pointing.setter
    def autofocus_use_current_pointing(self, value):
        self._autofocus_use_current_pointing = bool(value)
        self._config['autofocus_use_current_pointing'] = str(self._autofocus_use_current_pointing)
    
    @property
    def autofocus_timeout(self):
        return self._autofocus_timeout
    @autofocus_timeout.setter
    def autofocus_timeout(self, value):
        self._autofocus_timeout = float(value)
        self._config['autofocus_timeout'] = str(self._autofocus_timeout)

    @property
    def wait_for_scan_start_time(self):
        return self._wait_for_scan_start_time
    @wait_for_scan_start_time.setter
    def wait_for_scan_start_time(self, value):
        self._wait_for_scan_start_time = bool(value)
        self._config['wait_for_scan_start_time'] = str(self._wait_for_scan_start_time)

    @property
    def max_scan_late_time(self):
        return self._max_scan_late_time
    @max_scan_late_time.setter
    def max_scan_late_time(self, value):
        if value < 0: 
            value = 1e99
        self._max_scan_late_time = float(value)
        self._config['max_scan_late_time'] = str(self._max_scan_late_time)

    @property
    def preslew_time(self):
        return self._preslew_time
    @preslew_time.setter
    def preslew_time(self, value):
        self._preslew_time = float(value)
        self._config['preslew_time'] = str(self._preslew_time)

    @property
    def recenter_filters(self):
        return self._recenter_filters
    @recenter_filters.setter
    def recenter_filters(self, value):
        self._recenter_filters = iter(value)
        for v in value:
            self._config['recenter_filters'] += (str(v) + ',')
    
    @property
    def recenter_initial_offset_dec(self):
        return self._recenter_initial_offset_dec
    @recenter_initial_offset_dec.setter
    def recenter_initial_offset_dec(self, value):
        self._recenter_initial_offset_dec = float(value)
        self._config['recenter_initial_offset_dec'] = str(self._recenter_initial_offset_dec)
    
    @property
    def recenter_check_and_refine(self):
        return self._recenter_check_and_refine
    @recenter_check_and_refine.setter
    def recenter_check_and_refine(self, value):
        self._recenter_check_and_refine = bool(value)
        self._config['recenter_check_and_refine'] = str(self._recenter_check_and_refine)
    
    @property
    def recenter_max_attempts(self):
        return self._recenter_max_attempts
    @recenter_max_attempts.setter
    def recenter_max_attempts(self, value):
        self._recenter_max_attempts = int(value)
        self._config['recenter_max_attempts'] = str(self._recenter_max_attempts)

    @property
    def recenter_tolerance(self):
        return self._recenter_tolerance
    @recenter_tolerance.setter
    def recenter_tolerance(self, value):
        self._recenter_tolerance = float(value)
        self._config['recenter_tolerance'] = str(self._recenter_tolerance)

    @property
    def recenter_exposure(self):
        return self._recenter_exposure
    @recenter_exposure.setter
    def recenter_exposure(self, value):
        self._recenter_exposure = float(value)
        self._config['recenter_exposure'] = str(self._recenter_exposure)
    
    @property
    def recenter_save_images(self):
        return self._recenter_save_images
    @recenter_save_images.setter
    def recenter_save_images(self, value):
        self._recenter_save_images = bool(value)
        self._config['recenter_save_images'] = str(self._recenter_save_images)

    @property
    def recenter_save_path(self):
        return self._recenter_save_path
    @recenter_save_path.setter
    def recenter_save_path(self, value):
        self._recenter_save_path = value
        self._config['recenter_save_path'] = str(self._recenter_save_path)
    
    @property
    def recenter_sync_mount(self):
        return self._recenter_sync_mount
    @recenter_sync_mount.setter
    def recenter_sync_mount(self, value):
        self._recenter_sync_mount = bool(value)
        self._config['recenter_sync_mount'] = str(self._recenter_sync_mount)

    @property
    def hardware_timeout(self):
        return self._hardware_timeout
    @hardware_timeout.setter
    def hardware_timeout(self, value):
        self._hardware_timeout = float(value)
        self._config['hardware_timeout'] = str(self._hardware_timeout)
    
    @property
    def wcs_filters(self):
        return self._wcs_filters
    @wcs_filters.setter
    def wcs_filters(self, value):
        self._wcs_filters = iter(value)
        for v in value:
            self._config['wcs_filters'] += (str(v) + ',')

    @property
    def wcs_timeout(self):
        return self._wcs_timeout
    @wcs_timeout.setter
    def wcs_timeout(self, value):
        self._wcs_timeout = float(value)
        self._config['wcs_timeout'] = str(self._wcs_timeout)

class TelrunFile:
    def __init__(self, filename, scans=None):
        self._filename = filename
        self._scans = scans

        if os.path.isfile(self.filename):
            self._read_file()
        elif self.scans is not None:
            self._write_file()
        else: 
            raise TelrunError('Telrun file does not exist and no scans provided')
    
    def update_status_code(self, scan_index, status, message=None):
        self.scans[scan_index].status = status
        self.scans[scan_index].status_message = message
        self._write_file()
        
    def _read_file(self):
        with open(self.filename, 'r') as f:
            lines = f.readlines()

        if len(lines) % 25 != 0:
            raise TelrunError('Telrun file is not formatted correctly')
        
        scans = []
        for i in range(len(lines)//25):
            scan = TelrunScan()
            scan.read_lines(lines[i*25:(i+1)*25])
            scans.append(scan)
        self._scans = scans

    def _write_file(self):
        with open(self.filename, 'w') as f:
            for scan in self.scans:
                f.write(str(scan))

    @property
    def filename(self):
        return self._filename
    
    @property
    def scans(self):
        return self._scans

class TelrunScan:
    def __init__(self, filename='image.fts', status='N', status_message='',
                    observer='', obscode='', title='', target_name='',
                    skycoord=None, start_time=None,
                    interrupt_allowed=True, posx=None, posy=None,
                    binx=1, biny=1, startx=0, starty=0, numx=0,
                    numy=0, readout=0, exposure=0, light=True,
                    filter=''):

        self._filename = None
        self._status = None
        self._status_message = None
        self._observer = None
        self._obscode = None
        self._title = None
        self._target_name = None
        self._skycoord = None
        self._start_time = None
        self._interrupt_allowed = None
        self._posx = None
        self._posy = None
        self._binx = None
        self._biny = None
        self._startx = None
        self._starty = None
        self._numx = None
        self._numy = None
        self._readout = None
        self._exposure = None
        self._light = None
        self._filt = None

        self.filename = filename
        self.status = status
        self.status_message = status_message
        self.observer = observer
        self.obscode = obscode
        self.title = title
        self.target_name = target_name
        self.interrupt_allowed = interrupt_allowed
        self.posx = posx
        self.posy = posy
        self.binx = binx
        self.biny = biny
        self.startx = startx
        self.starty = starty
        self.numx = numx
        self.numy = numy
        self.readout = readout
        self.exposure = exposure
        self.light = light
        self.filt = filt
    
    def __str__(self):
        s =  'filename: %s\n' % self.filename
        s += 'status: %s\n' % self.status
        s += 'status_message: %s\n' % self.status_message
        s += 'observer: %s\n' % self.observer
        s += 'obscode: %s\n' % self.obscode
        s += 'title: %s\n' % self.title
        s += 'target_name: %s\n' % self.target_name
        try: 
            s += 'skycoord: %s\n' % self.skycoord.to_string('hmsdms')
        except:
            s += 'skycoord: None\n'
        try: 
            s += 'pm_ra_cosdec: %s\n' % self.skycoord.pm_ra_cosdec.to_string(u.arcsec/u.hour)
        except:
            s += 'pm_ra_cosdec: 0\n'
        try: 
            s += 'pm_dec: %s\n' % self.skycoord.pm_dec.to_string(u.arcsec/u.hour)
        except:
            s += 'pm_dec: 0\n'
        try: 
            s += 'frame: %s\n' % self.skycoord.frame.name
        except:
            s += 'frame: None\n'
        try: 
            s += 'start_time: %s\n' % self.start_time.fits
        except:
            s += 'start_time: None\n'
        s += 'interrupt_allowed: %s\n' % self.interrupt_allowed
        s += 'posx: %s\n' % self.posx
        s += 'posy: %s\n' % self.posy
        s += 'binx: %s\n' % self.binx
        s += 'biny: %s\n' % self.biny
        s += 'startx: %s\n' % self.startx
        s += 'starty: %s\n' % self.starty
        s += 'numx: %s\n' % self.numx
        s += 'numy: %s\n' % self.numy
        s += 'readout: %s\n' % self.readout
        s += 'exposure: %s\n' % self.exposure
        s += 'light: %s\n' % self.light
        s += 'filt: %s\n' % self.filt
    
    def read_lines(self, lines):
        if len(lines) != 25:
            raise TelrunError('Scan lines must be 24 lines long')
        
        self.filename = lines[0].split(': ')[-1]
        self.status = lines[1].split(': ')[-1]
        self.status_message = lines[2].split(': ')[-1]
        self.observer = lines[3].split(': ')[-1]
        self.obscode = lines[4].split(': ')[-1]
        self.title = lines[5].split(': ')[-1]
        self.target_name = lines[6].split(': ')[-1]

        coords = lines[7].split(': ')[-1]
        pm_ra_cosdec = float(lines[8].split(': ')[-1].split(' ')[0])
        pm_dec = float(lines[9].split(': ')[-1].split(' ')[0])
        frame = lines[10].split(': ')[-1]

        if 'None' not in (coords, pm_ra_cosdec, pm_dec, frame):
            self.skycoord = coord.SkyCoord(coords, 
                pm_ra_cosdec=pm_ra_cosdec*u.arcsec/u.hour, 
                pm_dec=pm_dec*u.arcsec/u.hour, 
                frame=frame)
        else:
            self.skycoord = None
        
        start_time = lines[11].split(': ')[-1]
        if 'None' not in start_time:
            self.start_time = astrotime.Time(start_time, format='fits')
        else:
            self.start_time = None
        
        self.interrupt_allowed = bool(lines[12].split(': ')[-1] in ('True', 'true', 'T', 't', '1'))
        self.posx = int(lines[13].split(': ')[-1])
        self.posy = int(lines[14].split(': ')[-1])
        self.binx = int(lines[15].split(': ')[-1])
        self.biny = int(lines[16].split(': ')[-1])
        self.startx = int(lines[17].split(': ')[-1])
        self.starty = int(lines[18].split(': ')[-1])
        self.numx = int(lines[19].split(': ')[-1])
        self.numy = int(lines[20].split(': ')[-1])
        self.readout = int(lines[21].split(': ')[-1])
        self.exposure = float(lines[22].split(': ')[-1])
        self.light = bool(lines[23].split(': ')[-1] in ('True', 'true', 'T', 't', '1'))
        self.fil = lines[24].split(': ')[-1]
    
    @property
    def filename(self):
        return self._filename
    @filename.setter
    def filename(self, value):
        self._filename = str(value)
        if self._filename.split('.')[1] not in ('fts', 'fit', 'fits'):
            self._filename = self._filename.split('.')[0] + '.fts'
    
    @property
    def status(self):
        return self._status
    @status.setter
    def status(self, value):
        if value not in ('N', 'D', 'F'):
            raise ValueError('status must be one of N, D, F')
        self._status = value
    
    @property
    def status_message(self):
        return self._status_message
    @status_message.setter
    def status_message(self, value):
        self._status_message = str(value)

    @property
    def observer(self):
        return self._observer
    @observer.setter
    def observer(self, value):
        self._observer = str(value)
    
    @property
    def obscode(self):
        return self._obscode
    @obscode.setter
    def obscode(self, value):
        self._obscode = str(value)

    @property
    def title(self):
        return self._title
    @title.setter
    def title(self, value):
        self._title = str(value)

    @property
    def target_name(self):
        return self._target_name
    @target_name.setter
    def target_name(self, value):
        self._target_name = str(value)

    @property
    def skycoord(self):
        return self._skycoord
    @skycoord.setter
    def skycoord(self, value):
        self._skycoord = coord.SkyCoord(value)

    @property
    def start_time(self):
        return self._start_time
    @start_time.setter
    def start_time(self, value):
        self._start_time = astrotime.Time(value)

    @property
    def interrupt_allowed(self):
        return self._interrupt_allowed
    @interrupt_allowed.setter
    def interrupt_allowed(self, value):
        self._interrupt_allowed = bool(value)
    
    @property
    def posx(self):
        return self._posx
    @posx.setter
    def posx(self, value):
        self._posx = int(value)

    @property
    def posy(self):
        return self._posy
    @posy.setter
    def posy(self, value):
        self._posy = int(value)

    @property
    def binx(self):
        return self._binx
    @binx.setter
    def binx(self, value):
        self._binx = int(value)
    
    @property
    def biny(self):
        return self._biny
    @biny.setter
    def biny(self, value):
        self._biny = int(value)
    
    @property
    def startx(self):
        return self._startx
    @startx.setter
    def startx(self, value):
        self._startx = int(value)

    @property
    def starty(self):
        return self._starty
    @starty.setter
    def starty(self, value):
        self._starty = int(value)

    @property
    def numx(self):
        return self._numx
    @numx.setter
    def numx(self, value):
        self._numx = int(value)

    @property
    def numy(self):
        return self._numy
    @numy.setter
    def numy(self, value):
        self._numy = int(value)

    @property
    def readout(self):
        return self._readout
    @readout.setter
    def readout(self, value):
        self._readout = int(value)
        
    @property
    def exposure(self):
        return self._exposure
    @exposure.setter
    def exposure(self, value):
        self._exposure = float(value)

    @property
    def light(self):
        return self._light
    @light.setter
    def light(self, value):
        self._light = bool(value)
        
    @property
    def filt(self):
        return self._filt
    @filter.setter
    def filt(self, value):
        self._filt = str(value)

class TelrunGUI(ttk.Frame):
    def __init__(self, parent, TelrunOperator):
        ttk.Frame.__init__(self, parent)
        self._parent = parent
        self._telrun = TelrunOperator

        self._build_gui()
        self._update()
    
    def _build_gui(self):
        ttk.Label(self, text='System Status', font=_gui_font).grid(row=0, column=0, columnspan=3, sticky='new')
        self.system_status_widget = _SystemStatusWidget(self)
        self.system_status_widget.grid(row=1, column=0, columnspan=3, sticky='sew')

        ttk.Label(self, text='Previous Scan', font=_gui_font).grid(row=2, column=0, columnspan=1, sticky='sew')
        self.previous_scan_widget = _ScanWidget(self)
        self.previous_scan_widget.grid(row=3, column=0, columnspan=1, sticky='new')

        ttk.Label(self, text='Current Scan', font=_gui_font).grid(row=2, column=1, columnspan=1, sticky='sew')
        self.current_scan_widget = _ScanWidget(self)
        self.current_scan_widget.grid(row=3, column=1, columnspan=1, sticky='new')

        ttk.Label(self, text='Next Scan', font=_gui_font).grid(row=2, column=2, columnspan=1, sticky='sew')
        self.next_scan_widget = _ScanWidget(self)
        self.next_scan_widget.grid(row=3, column=2, columnspan=1, sticky='new')

        self.log_text = ScrolledText(self, width=80, height=20, state='disabled')
        self.log_text.grid(column=0, row=4, columnspan=3, sticky='new')

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, weight=1)

        log_handler = _TextHandler(self.log_text)
        log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        log_handler.setFormatter(log_formatter)
        logger.addHandler(log_handler)
    
    def _update(self):
        self.system_status_widget.update()
        self.previous_scan_widget.update(self._telrun.previous_scan)
        self.current_scan_widget.update(self._telrun.current_scan)
        self.next_scan_widget.update(self._telrun.next_scan)

        self.after(1000, self._update)

class _SystemStatusWidget(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self._parent = parent

        self.build_gui()
        self.update()
    
    def build_gui(self):
        
        rows0 = _Rows(self, 0)
        self.sun_elevation = rows0.add_row('Sun Elevation:')
        self.moon_elevation = rows0.add_row('Moon Elevation:')
        self.moon_illumination = rows0.add_row('Moon Illumination:')
        self.lst = rows0.add_row('LST:')
        self.ut = rows0.add_row('UT:')
        self.last_autofocus_time = rows0.add_row('Last Autofocus Time:')
        self.time_until_next_autofocus = rows0.add_row('Time Until Next Autofocus:')
        self.last_scan_status = rows0.add_row('Last Scan Status:')
        self.current_scan_index = rows0.add_row('Current Scan Index:')
        self.time_until_scan_start = rows0.add_row('Time Until Scan Start:')
        self.skipped_scan_count = rows0.add_row('Skipped Scan Count:')
        self.total_scan_count = rows0.add_row('Total Scan Count:')

        rows1 = _Rows(self, 2)
        self.autofocus_status = rows1.add_row('Autofocus Status:')
        self.camera_status = rows1.add_row('Camera Status:')
        self.cover_calibrator_status = rows1.add_row('Cover Calibrator Status:')
        self.dome_status = rows1.add_row('Dome Status:')
        self.filter_wheel_status = rows1.add_row('Filter Wheel Status:')
        self.focuser_status = rows1.add_row('Focuser Status:')
        self.observing_conditions_status = rows1.add_row('Observing Conditions Status:')
        self.rotator_status = rows1.add_row('Rotator Status:')
        self.safety_monitor_status = rows1.add_row('Safety Monitor Status:')
        self.switch_status = rows1.add_row('Switch Status:')
        self.telescope_status = rows1.add_row('Telescope Status:')
        self.wcs_status = rows1.add_row('WCS Status:')

        rows2 = _Rows(self, 4)
        self.cloud_cover = rows2.add_row('Cloud Cover:')
        self.dew_point = rows2.add_row('Dew Point:')
        self.humidity = rows2.add_row('Humidity:')
        self.pressure = rows2.add_row('Pressure:')
        self.rainrate = rows2.add_row('Rain Rate:')
        self.sky_brightness = rows2.add_row('Sky Brightness:')
        self.sky_quality = rows2.add_row('Sky Quality:')
        # self.sky_temperature = rows2.add_row('Sky Temperature:')
        self.star_fwhm = rows2.add_row('Star FWHM:')
        self.temperature = rows2.add_row('Temperature:')
        self.wind_direction = rows2.add_row('Wind Direction:')
        self.wind_gust = rows2.add_row('Wind Gust:')
        self.wind_speed = rows2.add_row('Wind Speed:')

        rows3 = _Rows(self, 6)
        self.wait_for_sun = rows3.add_row('Wait For Sun:')
        self.max_solar_elev = rows3.add_row('Max Solar Elevation:')
        self.wait_for_cooldown = rows3.add_row('Wait For Cooldown:')
        self.default_readout = rows3.add_row('Default Readout:')
        self.autofocus_interval = rows3.add_row('Autofocus Interval:')
        self.autofocus_filters = rows3.add_row('Autofocus Filters:')
        self.autofocus_use_current_pointing = rows3.add_row('Autofocus Use Current Pointing:')
        self.wait_for_scan_start_time = rows3.add_row('Wait For Scan Start Time:')
        self.max_scan_late_time = rows3.add_row('Max Scan Late Time:')
        self.preslew_time = rows3.add_row('Preslew Time:')
        self.recenter_filters = rows3.add_row('Recenter Filters:')
        self.wcs_filters = rows3.add_row('WCS Filters:')

    def update(self):
        self.sun_elevation.set(self._parent._telrun.observatory.sun_altaz()[0])
        self.moon_elevation.set(self._parent._telrun.observatory.moon_altaz()[0])
        self.moon_illumination.set(self._parent._telrun.observatory.moon_illumination())
        self.lst.set(self._parent._telrun.observatory.lst())
        self.ut.set(self._parent._telrun.observatory.observatory_time.iso)
        self.last_autofocus_time.set(astrotime.Time(self._parent._telrun.last_autofocus_time, format='unix').iso)
        self.time_until_next_autofocus.set(self._parent._telrun.last_autofocus_time + self._parent._telrun.autofocus_interval - Time.now())
        self.last_scan_status.set(self._parent._telrun.previous_scan.status)
        self.current_scan_index.set(self._parent._telrun.current_scan_index)
        self.time_until_scan_start.set((self._parent._telrun.current_scan.start_time - astrotime.Time.now()).sec)
        self.skipped_scan_count.set(self._parent._telrun.skipped_scan_count)
        self.total_scan_count.set(len(self._parent._telrun._telrun_file.scans))

        self.autofocus_status.set(self._parent._telrun.autofocus_status)
        self.camera_status.set(self._parent._telrun.camera_status)
        self.cover_calibrator_status.set(self._parent._telrun.cover_calibrator_status)
        self.dome_status.set(self._parent._telrun.dome_status)
        self.filter_wheel_status.set(self._parent._telrun.filter_wheel_status)
        self.focuser_status.set(self._parent._telrun.focuser_status)
        self.observing_conditions_status.set(self._parent._telrun.observing_conditions_status)
        self.rotator_status.set(self._parent._telrun.rotator_status)
        self.safety_monitor_status.set(self._parent._telrun.safety_monitor_status)
        self.switch_status.set(self._parent._telrun.switch_status)
        self.telescope_status.set(self._parent._telrun.telescope_status)
        self.wcs_status.set(self._parent._telrun.wcs_status)

        self.cloud_cover.set(self._parent._telrun.observing_conditions.CloudCover)
        self.dew_point.set(self._parent._telrun.observing_conditions.DewPoint)
        self.humidity.set(self._parent._telrun.observing_conditions.Humidity)
        self.pressure.set(self._parent._telrun.observing_conditions.Pressure)
        self.rainrate.set(self._parent._telrun.observing_conditions.RainRate)
        self.sky_brightness.set(self._parent._telrun.observing_conditions.SkyBrightness)
        self.sky_quality.set(self._parent._telrun.observing_conditions.SkyQuality)
        # self.sky_temperature.set(self._parent._telrun.observing_conditions.SkyTemperature)
        self.star_fwhm.set(self._parent._telrun.observing_conditions.StarFWHM)
        self.temperature.set(self._parent._telrun.observing_conditions.Temperature)
        self.wind_direction.set(self._parent._telrun.observing_conditions.WindDirection)
        self.wind_gust.set(self._parent._telrun.observing_conditions.WindGust)
        self.wind_speed.set(self._parent._telrun.observing_conditions.WindSpeed)

        self.wait_for_sun.set(str(self._parent._telrun.wait_for_sun))
        self.max_solar_elev.set(str(self._parent._telrun.max_solar_elev))
        self.wait_for_cooldown.set(str(self._parent._telrun.wait_for_cooldown))
        self.default_readout.set(str(self._parent._telrun.default_readout))
        self.autofocus_interval.set(str(self._parent._telrun.autofocus_interval))

        auto_filt = ''
        for filt in self._parent._telrun.autofocus_filters:
            auto_filt += filt + ', '
        self.autofocus_filters.set(auto_filt)

        self.autofocus_use_current_pointing.set(str(self._parent._telrun.autofocus_use_current_pointing))
        self.wait_for_scan_start_time.set(str(self._parent._telrun.wait_for_scan_start_time))
        self.max_scan_late_time.set(str(self._parent._telrun.max_scan_late_time))
        self.preslew_time.set(str(self._parent._telrun.preslew_time))

        recenter_filt = ''
        for filt in self._parent._telrun.recenter_filters:
            recenter_filt += filt + ', '
        self.recenter_filters.set(recenter_filt)

        wcs_filt = ''
        for filt in self._parent._telrun.wcs_filters:
            wcs_filt += filt + ', '
        self.wcs_filters.set(wcs_filt)

class _ScanWidget(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self._parent = parent

        self.build_gui()
        self.update()
    
    def build_gui(self):
        rows = _Rows(self, 0)

        self.filename = rows.add_row('Filename:')
        self.status = rows.add_row('Status:')
        self.status_message = rows.add_row('Status Message:')
        self.observer = rows.add_row('Observer:')
        self.obscode = rows.add_row('Observer Code:')
        self.title = rows.add_row('Title:')
        self.target_name = rows.add_row('Target Name:')
        self.skycoord = rows.add_row('SkyCoord:')
        self.proper_motion = rows.add_row('Proper Motion:')
        self.start_time = rows.add_row('Start Time:')
        self.interrupt_allowed = rows.add_row('Interrupt Allowed:')
        self.pos = rows.add_row('Requested Repositioning:')
        self.binning = rows.add_row('Binning:')
        self.subframe_start = rows.add_row('Subframe Start:')
        self.subframe_size = rows.add_row('Subframe Size:')
        self.readout = rows.add_row('Readout Mode:')
        self.exposure = rows.add_row('Exposure Time (s):')
        self.light = rows.add_row('Shutter Open:')
        self.filt = rows.add_row('Filter:')

    def update(self, scan):
        if scan is None:
            self.filename.set('')
            self.status.set('')
            self.status_message.set('')
            self.observer.set('')
            self.obscode.set('')
            self.title.set('')
            self.target_name.set('')
            self.skycoord.set('')
            self.proper_motion.set('')
            self.start_time.set('')
            self.interrupt_allowed.set('')
            self.pos.set('')
            self.binning.set('')
            self.subframe_start.set('')
            self.subframe_size.set('')
            self.readout.set('')
            self.exposure.set('')
            self.light.set('')
            self.filt.set('')

        else:
            self.filename.set(scan.filename)
            self.status.set(scan.status)
            self.status_message.set(scan.status_message)
            self.observer.set(scan.observer)
            self.obscode.set(scan.obscode)
            self.title.set(scan.title)
            self.target_name.set(scan.target_name)
            self.skycoord.set(scan.skycoord.to_string('hmsdms'))
            self.proper_motion.set(scan.skycoord.pm_ra_cosdec.to_string(u.arcsec/u.hour) + ' ' + scan.skycoord.pm_dec.to_string(u.arcsec/u.hour))
            self.start_time.set(scan.start_time.fits)
            self.interrupt_allowed.set(scan.interrupt_allowed)
            self.pos.set(str(scan.posx) + ', ' + str(scan.posy))
            self.binning.set(str(scan.binx) + 'x' + str(scan.biny))
            self.subframe_start.set(str(scan.startx) + ', ' + str(scan.starty))
            self.subframe_size.set(str(scan.numx) + 'x' + str(scan.numy))
            self.readout.set(scan.readout)
            self.exposure.set(scan.exposure)
            self.light.set(scan.light)
            self.filt.set(scan.filt)
class _Rows:
    def __init__(self, parent, column):
        self._parent = parent
        self._column = column
        self._next_row = 0

    def add_row(self):
        label = ttk.Label(self._parent, text=label_text)
        label.grid(column=self._column, row=self._next_row, sticky='e')

        string_var = tk.StringVar()
        entry = ttk.Entry(self._parent, textvariable=string_var)
        entry.grid(column=self._column+1, row=self._next_row, sticky='ew')

        self._next_row += 1

        return string_var

class _TextHandler(logging.Handler):
    # This class allows you to log to a Tkinter Text or ScrolledText widget
    # Adapted from Moshe Kaplan: https://gist.github.com/moshekaplan/c425f861de7bbf28ef06

    def __init__(self, text):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Store a reference to the Text it will log to
        self.text = text

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text.configure(state='normal')
            self.text.insert(tk.END, msg + '\n')
            self.text.configure(state='disabled')
            # Autoscroll to the bottom
            self.text.yview(tk.END)
        # This is necessary because we can't modify the Text from other threads
        self.text.after(0, append)

class TelrunError(Exception):
    pass

def setup_telrun_observatory(telhome):
    pass

def summary_report(sls_file, report_file):
    if type(sls_file) is str:
        sls_file = TelrunFile(sls_file)
    elif type(sls_file) is not TelrunFile:
        raise TypeError('sls_file must be a string or TelrunFile object')