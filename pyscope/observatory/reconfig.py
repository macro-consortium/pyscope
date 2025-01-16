"""A module to calculate reconfiguration times of an observatory based on a configuration file."""

import configparser
from astropy.coordinates import HADec
import astropy.units as u
from astroplan import Observer


class ReconfigConfigs:
    """
    A class to calculate reconfiguration times of an observatory based on a configuration file.
    While not strictly necessary to compute reconfiguration times, the location of the observatory
    is required to calculate slew times by first finding in HA/Dec coordinates.
    The time of the observation is also required to calculate the HA/Dec coordinates.

    Attributes:
    -----------
    filter_wheels : dict
        A dictionary to store filter wheel configurations, keyed by wheel ID.
    telescope : Telescope
        An instance of the Telescope class configured from a config file.
    camera : Camera
        An instance of the Camera class configured from a config file.
    focuser : Focuser
        An instance of the Focuser class configured from a config file.
    auxiliary_systems : AuxiliarySystems
        An instance of the Other class configured from a config file.

    Methods:
    --------
    __init__(config_path)
        Initializes the ReconfigConfigs instance with the provided configuration.
    """

    def __init__(self, config_path):
        """
        Initializes the ReconfigConfigs instance with the provided configuration file.

        Parameters:
        -----------
        config_path : str
            The path to the configuration file to read.
        """
        config = configparser.ConfigParser(inline_comment_prefixes="#")
        config.read(config_path)

        # Initialize the filter wheel(s)
        self.filter_wheels = {}
        for section in config.sections():
            if section.startswith("filter_wheel_"):
                wheel_id = section.split("_")[-1]
                self.filter_wheels[wheel_id] = FilterWheel(config, section)

        # Initialize the telescope, camera, focuser, and other configurations
        self.telescope = Telescope(config)
        self.camera = Camera(config)
        self.focuser = Focuser(config)
        self.aux = AuxiliarySystems(config)

    def calc_reconfig_time_blocks(
        self, first_block, second_block, location, simultaneous=False, verbose=False
    ):
        """Calculate the reconfiguration time for the observatory between two blocks

        Parameters
        ----------
        first_block (Block): The first block to reconfigure to
        second_block (Block): The second block to reconfigure to
        simultaneous (bool): Whether to perform the reconfiguration tasks simultaneously
        """
        # Calculate the reconfiguration time for the telescope
        # Should we reposition?
        try:
            repositioning = not (second_block["repositioning"] == (0,0))
        except AttributeError:
            repositioning = not (second_block["repositioning"].data == [0,0]).all()

        reconfig_time = self.calc_reconfig_time(
            first_block["target"],
            second_block["target"],
            obs_location=location,
            obs_time=first_block["start_time"],
            current_filter_pos=first_block["filter"],
            target_filter_pos=second_block["filter"],
            repositioning=repositioning,
            simultaneous=simultaneous,
            verbose=verbose
        )

        return reconfig_time

    def calc_reconfig_time(
        self,
        current_coords,
        target_coords,
        obs_location=None,
        obs_time=None,
        current_filter_pos=None,
        target_filter_pos=None,
        repositioning=False,
        simultaneous=False,
        verbose=False
    ):
        """Calculate the reconfiguration time for the observatory

        Parameters
        ----------
        current_coords (astropy.coordinates.SkyCoord): The current telescope coordinates
        target_coords (astropy.coordinates.SkyCoord): The target telescope coordinates
        obs_location (astropy.coordinates.EarthLocation): The observation location
        obs_time (astropy.time.Time): The observation time
        current_filter_pos (int): The current filter wheel position
        target_filter_pos (int): The target filter wheel position
        simultaneous (bool): Whether to perform the reconfiguration tasks simultaneously
        verbose (bool): Whether to print the reconfiguration times for each component

        Returns
        -------
        reconfig_time (float): The total reconfiguration time in seconds
        """
        # If obs_location is not an EarthLocation, convert it to one
        if isinstance(obs_location, Observer):
            if verbose:
                print(f"Is Observer: {obs_location}")
            obs_location = obs_location.location

        # Calculate the slew time for the telescope
        slew_time = self.telescope.calc_slew_time_skycoord(
            current_coords,
            target_coords,
            obs_location=obs_location,
            obs_time=obs_time,
            return_quantity=True,
        )

        # Calculate the filter wheel change time
        filter_change_time = 0.0 * u.s
        filter_offset = 0.0
        if current_filter_pos is not None and target_filter_pos is not None:
            filter_change_time = self.filter_wheels["1"].calculate_filter_change_time(
                current_filter_pos, target_filter_pos
            )
            filter_offset = self.filter_wheels["1"].filter_offset_dist(
                current_filter_pos, target_filter_pos
            )

        # Calculate camera overhead time
        camera_overhead_time = self.camera.download_time + self.camera.readout_time

        # Calculate focuser overhead time
        focuser_move_time = self.focuser.calc_focuser_move_time(filter_offset, verbose=verbose)

        # Calculate other overhead time
        other_overhead_time = 0.0 * u.s
        other_overhead_time += self.aux.pad_time
        if repositioning:
            other_overhead_time += self.aux.repositioning_time
        
        # Print the reconfiguration times for each component
        if verbose:
            print("Reconfiguration Times:")
            print(f"Slew Time: {slew_time}")
            print(f"Filter Change Time: {filter_change_time}")
            print(f"Camera Overhead Time: {camera_overhead_time}")
            print(f"Focuser Move Time: {focuser_move_time}")
            print(f"Other Overhead Time: {other_overhead_time}")

        # Calculate the total reconfiguration time
        if simultaneous:
            reconfig_time = max(
                slew_time,
                filter_change_time,
                camera_overhead_time,
                focuser_move_time,
                other_overhead_time,
            )
        else:
            reconfig_time = (
                slew_time
                + filter_change_time
                + camera_overhead_time
                + focuser_move_time
                + other_overhead_time
            )

        return reconfig_time


class FilterWheel:
    """A class to store filter wheel configuration parameters and calculate filter change times"""

    def __init__(self, config, section):
        self.unidirectional = config.getboolean(
            section, "unidirectional", fallback=True
        )
        self.pos_const = config.getfloat(section, "pos_const", fallback=0.0) * u.s
        self.pos_lin = config.getfloat(section, "pos_lin", fallback=0.0) * u.s
        self.num_positions = config.getint(section, "num_positions", fallback=5)
        self.filter_names = config.get(section, "filter_names", fallback="").split(",")
        self.filter_offsets = config.get(section, "filter_offsets", fallback="").split(
            ","
        )

    def calculate_filter_change_time(self, current_pos, target_pos):
        """Calculate the time to change the filter wheel position

        Parameters
        ----------
        current_pos (int): The current filter wheel position
        target_pos (int): The target filter wheel position

        Returns
        -------
        filter_change_time (float): The time to change the filter wheel position in seconds
        """
        filter_change_time = 0.0 * u.s

        try:
            current_pos = int(current_pos)
            target_pos = int(target_pos)
        except ValueError:
            current_pos = self.filter_names.index(current_pos)
            target_pos = self.filter_names.index(target_pos)

        if self.unidirectional:
            # Calculate the time to move to the target position
            if target_pos > current_pos:
                filter_change_time = (
                    target_pos - current_pos
                ) * self.pos_lin + self.pos_const
            elif target_pos < current_pos:
                filter_change_time = (
                    self.num_positions - current_pos + target_pos
                ) * self.pos_lin + self.pos_const
        else:
            raise NotImplementedError(
                "Bidirectional filter wheel change times are not yet implemented."
            )

        return filter_change_time

    def filter_offset_dist(self, current_pos, target_pos):
        """Calculate the filter offset distance between two filter wheel positions

        Parameters
        ----------
        current_pos (int): The current filter wheel position
        target_pos (int): The target filter wheel position

        Returns
        -------
        filter_offset_dist (float): The filter offset distance in microns
        """
        try:
            current_pos = int(current_pos)
            target_pos = int(target_pos)
        except ValueError:
            current_pos = self.filter_names.index(current_pos)
            target_pos = self.filter_names.index(target_pos)

        current_offset = float(self.filter_offsets[current_pos])
        target_offset = float(self.filter_offsets[target_pos])

        filter_offset_dist = target_offset - current_offset

        # Below should return units of the focuser units, rather than just a float
        return filter_offset_dist


class Telescope:
    """A class to store telescope configuration parameters and calculate slew times"""

    def __init__(self, config):
        self.type = config.get("telescope", "type", fallback="equatorial").lower()
        self.GEM = config.getboolean("telescope", "GEM", fallback=True)
        self.slew_speed_units = u.Unit(
            config.get("telescope", "slew_speed_units", fallback="deg/s")
        )
        self.RA_slew_speed = config.getfloat("telescope", "RA_slew_speed", fallback=0.0)
        self.DEC_slew_speed = config.getfloat(
            "telescope", "DEC_slew_speed", fallback=0.0
        )
        self.RA_acceleration = config.getfloat(
            "telescope", "RA_acceleration", fallback=0.0
        )
        self.DEC_acceleration = config.getfloat(
            "telescope", "DEC_acceleration", fallback=0.0
        )
        self.update_slew_units()
        self.settle_time = (
            config.getfloat("telescope", "settle_time", fallback=0.0) * u.s
        )
        self.backlash_comp_time = (
            config.getfloat("telescope", "backlash_comp_time", fallback=0.0) * u.s
        )

        self.RA_accel_distance, self.DEC_accel_distance = self.calc_accel_distances()

    def update_slew_units(self):
        """Update the units for RA and DEC slew speeds."""
        self.RA_slew_speed *= self.slew_speed_units
        self.DEC_slew_speed *= self.slew_speed_units
        self.RA_acceleration *= self.slew_speed_units / u.s
        self.DEC_acceleration *= self.slew_speed_units / u.s

    def calc_slew_time(self, ra_move, dec_move, return_quantity=False):
        """Calculate the slew time for the telescope given the RA and DEC move distances

        Parameters
        ----------
        ra_move (astropy.units.Quantity): The RA move distance
        dec_move (astropy.units.Quantity): The DEC move distance
        return_quantity (bool): Whether to return the time as an astropy Quantity

        Returns
        -------
        slew_time (float or astropy.units.Quantity):
            The slew time in seconds or as an astropy Quantity
        """
        ra_time = self.calc_single_slew_time(
            abs(ra_move),
            self.RA_slew_speed,
            self.RA_acceleration,
            self.RA_accel_distance,
            return_quantity=True,
        )
        dec_time = self.calc_single_slew_time(
            abs(dec_move),
            self.DEC_slew_speed,
            self.DEC_acceleration,
            self.DEC_accel_distance,
            return_quantity=True,
        )

        slew_time = max(ra_time, dec_time).to(u.s)
        slew_time += self.settle_time + self.backlash_comp_time

        if not return_quantity:
            slew_time = slew_time.value

        return slew_time

    def calc_single_slew_time(
        self, distance, max_speed, acceleration, accel_distance, return_quantity=False
    ):
        """Calculate the slew time for the telescope given the move distance,
        max speed, and acceleration

        Parameters
        ----------
        distance (astropy.units.Quantity): The move distance
        max_speed (astropy.units.Quantity): The maximum speed
        acceleration (astropy.units.Quantity): The acceleration
        return_quantity (bool): Whether to return the time as an astropy Quantity

        Returns
        -------
        slew_time (float or astropy.units.Quantity):
            The slew time in seconds or as an astropy Quantity
        """
        # If distance is above 2x the acceleration distance, the telescope will reach max speed
        if distance > 2 * accel_distance:
            remaining_distance = distance - 2 * accel_distance
            slew_time = (2 * max_speed / acceleration) + (
                remaining_distance / max_speed
            )
        else:
            slew_time = (2 * distance / acceleration) ** 0.5

        if not return_quantity:
            slew_time = slew_time.value

        return slew_time

    def calc_accel_distances(self):
        """Calculate the distance the telescope will travel while accelerating to
        the maximum slew speed in RA and DEC.
        """
        # Calculate the distance traveled while accelerating to the maximum slew speed
        ra_accel_time = self.RA_slew_speed / self.RA_acceleration
        dec_accel_time = self.DEC_slew_speed / self.DEC_acceleration

        ra_accel_distance = 0.5 * self.RA_acceleration * ra_accel_time**2
        dec_accel_distance = 0.5 * self.DEC_acceleration * dec_accel_time**2

        return ra_accel_distance, dec_accel_distance

    def calc_slew_time_skycoord(
        self,
        current_coord,
        target_coord,
        obs_location=None,
        obs_time=None,
        return_quantity=False,
    ):
        """Calculate the slew time for the telescope to move from the current to target coordinates.
        Exception if location and time are not provided (required for HA/Dec calculations) -
        should throw a warning instead in that case, and return the slew time in RA/Dec coordinates
        with the caveat that the slew time may not be accurate, as it may assume the telescope
        will travel in a straight line between the two points (possibly through the Earth).

        Parameters
        ----------
        current_coord (astropy.coordinates.SkyCoord): The current telescope coordinates
        target_coord (astropy.coordinates.SkyCoord): The target telescope coordinates
        obs_location (astropy.coordinates.EarthLocation): The observation location
        obs_time (astropy.time.Time): The observation time
        return_quantity (bool): Whether to return the time as an astropy Quantity

        Returns
        -------
        slew_time (float or astropy.units.Quantity):
            The slew time in seconds or as an astropy Quantity
        """
        if obs_location is None or obs_time is None:
            raise ValueError(
                "Observation location and time are required for HA/Dec calculations."
            )

        if self.type == "equatorial":
            frame = HADec(obstime=obs_time, location=obs_location)
            # Calculate HA/Dec coordinates for the current and target coordinates
            current_hadec = current_coord.transform_to(frame)
            target_hadec = target_coord.transform_to(frame)
            ra_move, dec_move = self.calc_slew_moves(current_hadec, target_hadec)
            slew_time = self.calc_slew_time(
                ra_move, dec_move, return_quantity=return_quantity
            )
        else:
            # Exception - only equatorial coordinates are supported
            raise ValueError(
                "Only equatorial coordinates are supported for slew time calculations currently."
            )

        return slew_time

    def calc_slew_moves(self, current_coord, target_coord):
        """Calculate the RA and DEC moves for the telescope to move from the
        current to target coordinates

        TODO: This function should be updated to handle the case where the telescope is a GEM
        and the target is on the other side of the meridian or anti-meridian.

        Parameters
        ----------
        current_coord (astropy.coordinates.SkyCoord): The current telescope coordinates (in HA/Dec)
        target_coord (astropy.coordinates.SkyCoord): The target telescope coordinates (in HA/Dec)

        Returns
        -------
        ha_move (astropy.units.Quantity): The HA move distance
        dec_move (astropy.units.Quantity): The DEC move distance
        """
        if self.type == "equatorial":
            if not self.GEM:
                ha_move = target_coord.ha - current_coord.ha
                dec_move = target_coord.dec - current_coord.dec
            else:
                raise ValueError(
                    "Only Fork Mount equatorial telescopes are supported for slew move calculations currently."
                )
        else:
            raise ValueError(
                "Only equatorial coordinates are supported for slew move calculations currently."
            )

        return ha_move, dec_move


class Camera:
    """A class to store camera configuration parameters"""

    def __init__(self, config):
        self.download_time = (
            config.getfloat("camera", "download_time", fallback=0.0) * u.s
        )
        self.readout_time = (
            config.getfloat("camera", "readout_time", fallback=0.0) * u.s
        )

    def calc_camera_time(self, exptime):
        """Calculate the time to capture an image with the camera"""
        return exptime * u.s + self.download_time + self.readout_time

    def calc_camera_overhead_time(self):
        """Calculate the overhead time for the camera"""
        return self.download_time + self.readout_time


class Focuser:
    """A class to store focuser configuration parameters"""

    def __init__(self, config):
        self.units = config.get("focuser", "units", fallback="steps")
        if "micron" in self.units:
            self.units = "micron"
        self.speed = config.getfloat("focuser", "speed", fallback=0.0) / u.s
        self.acceleration = (
            config.getfloat("focuser", "acceleration", fallback=0.0) / u.s / u.s
        )
        self.backlash_comp_distance = config.getfloat(
            "focuser", "backlash_comp_distance", fallback=0.0
        )
        self.backlash_comp_time = (
            config.getfloat("focuser", "backlash_comp_time", fallback=0.0) * u.s
        )

        self.update_move_units()

        self.accel_distance = self.calc_focuser_accel_distance()

    def update_move_units(self):
        """Update the units for the focuser speed and acceleration."""
        self.speed *= u.Unit(self.units)
        self.acceleration *= u.Unit(self.units)
        self.backlash_comp_distance *= u.Unit(self.units)

    def calc_focuser_move_time(self, position_offset, verbose=False):
        """Calculate the time to move the focuser to the target offset"""

        # If position offset is not a quantity with units, convert to the correct units
        if not isinstance(position_offset, u.Quantity):
            position_offset = position_offset * u.Unit(self.units)
        if verbose:
            print(f"Focuser position offset: {position_offset}")
        
        if position_offset == 0:
            return 0.0 * u.s

        # This doesn't work right with moves smaller than the backlash compensation distance
        move_distance = abs(position_offset)
        if self.backlash_comp_distance > 0:
            if position_offset > self.backlash_comp_distance:
                move_distance += self.backlash_comp_distance
        elif self.backlash_comp_distance < 0:
            if position_offset > self.backlash_comp_distance:
                move_distance += self.backlash_comp_distance

        if verbose:
            print(f"Move distance with backlash compensation: {move_distance}")

        if move_distance > 2 * self.accel_distance:
            remaining_distance = move_distance - 2 * self.accel_distance
            move_time = (2 * self.speed / self.acceleration) + (
                remaining_distance / self.speed
            )
        else:
            move_time = (2 * move_distance / self.acceleration) ** 0.5

        move_time += self.backlash_comp_time

        return move_time

    def calc_focuser_accel_distance(self):
        """Calculate the distance the focuser will travel while accelerating to
        the maximum slew speed"""
        accel_time = self.speed / self.acceleration
        accel_distance = 0.5 * self.acceleration * accel_time**2

        return accel_distance


class AuxiliarySystems:
    """A class to store other configuration parameters"""

    def __init__(self, config):
        self.dome_open_time = config.getfloat("other", "dome_open_time", fallback=0.0) * u.s
        self.dome_close_time = config.getfloat("other", "dome_close_time", fallback=0.0) * u.s
        self.repositioning_time = config.getfloat("other", "repositioning_time", fallback=0.0) * u.s
        self.pad_time = config.getfloat("other", "pad_time", fallback=0.0) * u.s


    def calc_dome_open_time(self):
        """Calculate the time to open the dome"""
        return self.dome_open_time

    def calc_dome_close_time(self):
        """Calculate the time to close the dome"""
        return self.dome_close_time
    
    def calc_repositioning_time(self):
        """Calculate the time to reposition the telescope"""
        return self.repositioning_time
    
    def calc_pad_time(self):
        """Calculate the padding time to add to each observation"""
        return self.pad_time
    

