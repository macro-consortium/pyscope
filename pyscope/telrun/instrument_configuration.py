import logging

logger = logging.getLogger(__name__)


class InstrumentConfiguration:
    def __init__(
        self,
        name="",
        description="",
        observatory_identifier="",
        nasmyth_port=None,
        focus_offset=None,
        position_angle_offset=None,
        filt=None,
        shutter_state=None,
        readout_mode=None,
        binning=None,
        frame_position=None,
        frame_size=None,
        cooler_on=None,
        cooler_setpoint=None,
        flat_screen_brightness=None,
        inherit_from="current",
        **kwargs,
    ):
        """
        A group of `~pyscope.telrun.Option` objects that define the configuration of the
        instrument being controlled by a `~pyscope.telrun.TelrunOperator`.

        The  `~pyscope.telrun.InstrumentConfiguration` object is used to define the current
        status of user-schedulable options for the `~pyscope.observatory.Observatory`
        instrument. These include common options like a filter wheel selection, the
        focus position, and the readout mode, among other options.

        If a user passes values for each keyword argument, the `~pyscope.telrun.InstrumentConfiguration`
        will be treated as a "requested" configuration that will be attached to a
        `~pyscope.telrun.Field` or `~pyscope.telrun.ScheduleBlock` object and applied to the
        instrument when the observation is executed.

        If a user passes an `~pyscope.telrun.Option` object for each keyword argument, the
        `~pyscope.telrun.InstrumentConfiguration` will be treated as the "current" configuration that
        will be contained in the `pyscope.telrun.TelrunOperator.instrument_configuration` property. This
        `~pyscope.telrun.InstrumentConfiguration` will be used to contain the current and default
        status of the instrument options and will be used to create the "requested" configurations
        for each `~pyscope.telrun.Field` or `~pyscope.telrun.ScheduleBlock` object that does not
        specify a complete `~pyscope.telrun.InstrumentConfiguration`.

        If a user passes a `None` value for a keyword argument (which is the default value for all keyword arguments), the
        `~pyscope.telrun.InstrumentConfiguration` will inherit from the `pyscope.telrun.TelrunOperator.instrument_configuration`
        property using the `~pyscope.telrun.InstrumentConfiguration.inherit_from` keyword argument to determine which parameter to
        inherit from the `~pyscope.telrun.Option` for each keyword argument.

        Parameters
        ----------
        name : `str`, default : ""
            The name of the `~pyscope.telrun.InstrumentConfiguration`. This is typically a human-readable
            name that describes the configuration and does not change the behavior of the
            instrument.

        description : `str`, default : ""
            A description of the `~pyscope.telrun.InstrumentConfiguration`. This is typically a human-readable
            description that describes the configuration and does not change the behavior of
            the instrument.

        observatory_identifier : `str`, default : ""
            The identifier for the observatory that this `~pyscope.telrun.InstrumentConfiguration` is
            associated with. This is typically a human-readable identifier that the observatory
            manager has set for their `~pyscope.observatory.Observatory` object. If a
            `~pyscope.telrun.Scheduler` will only ever be used with one `~pyscope.observatory.Observatory`
            object, this value is optional and will not impact the behavior of the `~pyscope.telrun.Scheduler`.

        nasmyth_port : `~pyscope.telrun.Option`, `int`, or `None`, default : `None`
            The nasmyth port to use for the observation. If `None`, the nasmyth port will be inherited
            from the `~pyscope.telrun.Option` in the `~pyscope.telrun.TelrunOperator.instrument_configuration`
            using the `~pyscope.telrun.InstrumentConfiguration.inherit_from` keyword argument. This is typically
            only relevant for larger telescopes that have multiple nasmyth ports.

        focus_offset : `~pyscope.telrun.Option`, `~astropy.units.Quantity`, or `None`, default : `None`
            The focus offset to use for the observation. If `None`, the focus offset will be inherited
            from the `~pyscope.telrun.Option` in the `~pyscope.telrun.TelrunOperator.instrument_configuration`
            using the `~pyscope.telrun.InstrumentConfiguration.inherit_from` keyword argument. This is typically
            only relevant for observatories with filters that are not parfocal.

        position_angle_offset : `~pyscope.telrun.Option`, `~astropy.units.Quantity`, or `None`, default : `None`
            The position angle offset to use for the observation. If `None`, the position angle offset will be inherited
            from the `~pyscope.telrun.Option` in the `~pyscope.telrun.TelrunOperator.instrument_configuration`
            using the `~pyscope.telrun.InstrumentConfiguration.inherit_from` keyword argument. This is useful for
            instruments that require a specific position angle for the observation, e.g., slit spectrographs.

        filt : `~pyscope.telrun.Option`, `int`, `str`, `list`, or `None`, default : `None`
            The filter to use for the observation. If `None`, the filter will be inherited
            from the `~pyscope.telrun.Option` in the `~pyscope.telrun.TelrunOperator.instrument_configuration`
            using the `~pyscope.telrun.InstrumentConfiguration.inherit_from` keyword argument. If an `int` is passed,
            the filter will be selected by the filter wheel index. If a `str` is passed, the filter will be selected
            by the filter name. A `list` can be passed for backends with multiple `~pyscope.observatory.FilterWheel`
            objects on the same backend of the `~pyscope.observatory.Observatory`.

        shutter_state : `~pyscope.telrun.Option`, `bool`, or `None`, default : `None`
            The state of the shutter for the observation. If `None`, the shutter state will be inherited
            from the `~pyscope.telrun.Option` in the `~pyscope.telrun.TelrunOperator.instrument_configuration`
            using the `~pyscope.telrun.InstrumentConfiguration.inherit_from` keyword argument. If `True`, the shutter
            will be open. If `False`, the shutter will be closed.

        readout_mode : `~pyscope.telrun.Option`, `int`, `str`, or `None`, default : `None`
            The readout mode to use for the observation. If `None`, the readout mode will be inherited
            from the `~pyscope.telrun.Option` in the `~pyscope.telrun.TelrunOperator.instrument_configuration`
            using the `~pyscope.telrun.InstrumentConfiguration.inherit_from` keyword argument. If an `int` is passed,
            the readout mode will be selected by the readout mode index. If a `str` is passed, the readout mode will be
            selected by the readout mode name, which is typically provided by the observatory manager.

        binning : `~pyscope.telrun.Option`, `tuple`, or `None`, default : `None`
            The binning to use for the observation. If `None`, the binning will be inherited
            from the `~pyscope.telrun.Option` in the `~pyscope.telrun.TelrunOperator.instrument_configuration`
            using the `~pyscope.telrun.InstrumentConfiguration.inherit_from` keyword argument. The binning is typically
            a `tuple` of the x and y binning factors and may not always be the same for both axes. However, the observatory
            manager will usually provide info on what binning factors are available for the instrument.

        frame_position : `~pyscope.telrun.Option`, `tuple`, or `None`, default : `None`
            The frame position to use for the observation. If `None`, the frame position will be inherited
            from the `~pyscope.telrun.Option` in the `~pyscope.telrun.TelrunOperator.instrument_configuration`
            using the `~pyscope.telrun.InstrumentConfiguration.inherit_from` keyword argument. The frame position is
            typically a `tuple` of the x and y pixel positions of the corner of the frame. This is useful for instruments
            with multiple detectors or an extremely large detector with long readout times and a small region of interest
            that would be beneficial to read out at a higher frame rate, e.g., exoplanet transit observations.

        frame_size : `~pyscope.telrun.Option`, `tuple`, or `None`, default : `None`
            The frame size to use for the observation. If `None`, the frame size will be inherited
            from the `~pyscope.telrun.Option` in the `~pyscope.telrun.TelrunOperator.instrument_configuration`
            using the `~pyscope.telrun.InstrumentConfiguration.inherit_from` keyword argument. The frame size is
            typically a `tuple` of the x and y pixel sizes of the frame. This is useful for instruments with multiple
            detectors or an extremely large detector with long readout times and a small region of interest that would
            be beneficial to read out at a higher frame rate, e.g., exoplanet transit observations.

        cooler_on : `~pyscope.telrun.Option`, `bool`, or `None`, default : `None`
            The state of the cooler for the observation. If `None`, the cooler state will be inherited
            from the `~pyscope.telrun.Option` in the `~pyscope.telrun.TelrunOperator.instrument_configuration`
            using the `~pyscope.telrun.InstrumentConfiguration.inherit_from` keyword argument. If `True`, the cooler
            will be on. If `False`, the cooler will be turned off. This is typically a setting only used in requests of
            `~pyscope.telrun.DarkField` objects for calibration testing.

        cooler_setpoint : `~pyscope.telrun.Option`, `~astropy.units.Quantity`, or `None`, default : `None`
            The setpoint temperature of the cooler for the observation. If `None`, the cooler setpoint will be inherited
            from the `~pyscope.telrun.Option` in the `~pyscope.telrun.TelrunOperator.instrument_configuration`
            using the `~pyscope.telrun.InstrumentConfiguration.inherit_from` keyword argument. This is typically a setting
            only used in requests of `~pyscope.telrun.DarkField` objects for producing dark images.

        flat_screen_brightness : `~pyscope.telrun.Option`, `int`, or `None`, default : `None`
            The brightness of the flat screen for the observation. If `None`, the flat screen brightness will be inherited
            from the `~pyscope.telrun.Option` in the `~pyscope.telrun.TelrunOperator.instrument_configuration`
            using the `~pyscope.telrun.InstrumentConfiguration.inherit_from` keyword argument. This is typically a setting
            only used in requests of `~pyscope.telrun.FlatField` objects for producing flat field images.

        inherit_from : `str`, default : "current", {"current", "default"}
            The parameter to inherit from the `~pyscope.telrun.Option` in the `~pyscope.telrun.TelrunOperator.instrument_configuration`
            for each keyword argument when applying a "requested" configuration to the instrument. If "current", the current configuration
            saved within the `~pyscope.telrun.Option` objects will be used. If "default", the default configuration set in each
            `~pyscope.telrun.Option` will be used.

        **kwargs : `dict`, default : {}
            Additional keyword arguments to pass to the instrument for the observation. These are typically
            instrument-specific settings that are not covered by the standard `~pyscope.telrun.Option` objects.

        """
        logger.debug(
            """InstrumentConfiguration(
            name=%s,
            description=%s,
            observatory_identifier=%s,
            nasmyth_port=%s,
            focus_offset=%s,
            position_angle_offset=%s,
            filt=%s,
            shutter_state=%s,
            readout_mode=%s,
            binning=%s,
            frame_position=%s,
            frame_size=%s,
            cooler_on=%s,
            cooler_setpoint=%s,
            flat_screen_brightness=%s,
            inherit_from=%s,
            kwargs=%s,
        )"""
            % (
                name,
                description,
                observatory_identifier,
                nasmyth_port,
                focus_offset,
                position_angle_offset,
                filt,
                shutter_state,
                readout_mode,
                binning,
                frame_position,
                frame_size,
                cooler_on,
                cooler_setpoint,
                flat_screen_brightness,
                inherit_from,
                kwargs,
            )
        )

        self._type = "telrun operator instrument configuration"

    @classmethod
    def from_string(
        self,
        string,
        name=None,
        description=None,
        observatory_identifier=None,
        nasmyth_port=None,
        focus_offset=None,
        position_angle_offset=None,
        filt=None,
        shutter_state=None,
        readout_mode=None,
        binning=None,
        frame_position=None,
        frame_size=None,
        cooler_on=None,
        cooler_setpoint=None,
        flat_screen_brightness=None,
        inherit_from=None,
        **kwargs,
    ):
        """
        Create a `~pyscope.telrun.InstrumentConfiguration` or a `list` of `~pyscope.telrun.InstrumentConfiguration` objects
        from a `str` representation of a `~pyscope.telrun.InstrumentConfiguration`. All optional parameters are used to
        override the parameters extracted from the `str` representation.

        Parameters
        ----------
        string : `str`, required

        name : `str`, default : `None`

        description : `str`, default : `None`

        observatory_identifier : `str`, default : `None`

        nasmyth_port : `~pyscope.telrun.Option`, `int`, or `None`, default : `None`

        focus_offset : `~pyscope.telrun.Option`, `~astropy.units.Quantity`, or `None`, default : `None`

        position_angle_offset : `~pyscope.telrun.Option`, `~astropy.units.Quantity`, or `None`, default : `None`

        filt : `~pyscope.telrun.Option`, `int`, `str`, `list`, or `None`, default : `None`

        shutter_state : `~pyscope.telrun.Option`, `bool`, or `None`, default : `None`

        readout_mode : `~pyscope.telrun.Option`, `int`, `str`, or `None`, default : `None`

        binning : `~pyscope.telrun.Option`, `tuple`, or `None`, default : `None`

        frame_position : `~pyscope.telrun.Option`, `tuple`, or `None`, default : `None`

        frame_size : `~pyscope.telrun.Option`, `tuple`, or `None`, default : `None`

        cooler_on : `~pyscope.telrun.Option`, `bool`, or `None`, default : `None`

        cooler_setpoint : `~pyscope.telrun.Option`, `~astropy.units.Quantity`, or `None`, default : `None`

        flat_screen_brightness : `~pyscope.telrun.Option`, `int`, or `None`, default : `None`

        inherit_from : `str`, default : "current", {"current", "default"}

        **kwargs : `dict`, default : {}

        """
        logger.debug(
            """InstrumentConfiguration.from_string(
            string=%s,
            name=%s,
            description=%s,
            observatory_identifier=%s,
            nasmyth_port=%s,
            focus_offset=%s,
            position_angle_offset=%s,
            filt=%s,
            shutter_state=%s,
            readout_mode=%s,
            binning=%s,
            frame_position=%s,
            frame_size=%s,
            cooler_on=%s,
            cooler_setpoint=%s,
            flat_screen_brightness=%s,
            inherit_from=%s,
            kwargs=%s,
        )"""
            % (
                string,
                name,
                description,
                observatory_identifier,
                nasmyth_port,
                focus_offset,
                position_angle_offset,
                filt,
                shutter_state,
                readout_mode,
                binning,
                frame_position,
                frame_size,
                cooler_on,
                cooler_setpoint,
                flat_screen_brightness,
                inherit_from,
                kwargs,
            )
        )

    def __str__(self):
        """
        Return a `str` representation of the `~pyscope.telrun.InstrumentConfiguration`.

        Returns
        -------
        `str`
            A `str` representation of the `~pyscope.telrun.InstrumentConfiguration`.
        """
        logger.debug("InstrumentConfiguration().__str__() = %s" % self)

    def __repr__(self):
        """
        Return a `str` representation of the `~pyscope.telrun.InstrumentConfiguration`.

        Returns
        -------
        `str`
            A `str` representation of the `~pyscope.telrun.InstrumentConfiguration`.
        """
        logger.debug("InstrumentConfiguration().__repr__() = %s" % self)
        return str(self)

    def __call__(self, instrument_configuration, inherit_from=None):
        """
        Update the `~pyscope.telrun.InstrumentConfiguration` object with the values from the
        `instrument_configuration` object that contain the new values to update the
        selection of options inside this `~pyscope.telrun.InstrumentConfiguration`. If the
        `inherit_from` keyword argument is passed, the `~pyscope.telrun.InstrumentConfiguration` object
        will override the default `inherit_from` value.

        If `inherit_from="current"`, the
        `~pyscope.telrun.InstrumentConfiguration` will inherit from the current configuration
        values saved in the `~pyscope.telrun.Option` objects. This is the default behavior of the class.
        If `inherit_from="default"`, the
        `~pyscope.telrun.InstrumentConfiguration` will inherit the `~pyscope.telrun.Option` default
        values to fill in the values that are not specified in the `instrument_configuration`.

        Parameters
        ----------
        instrument_configuration : `~pyscope.telrun.InstrumentConfiguration`, required
            The `~pyscope.telrun.InstrumentConfiguration` object that contains the new values to update
            the selection of options inside this `~pyscope.telrun.InstrumentConfiguration`.

        inherit_from : `str`, default : `None`, {"current", "default"}
            The parameter to inherit from the `~pyscope.telrun.Option` in the `instrument_configuration`
            for each keyword argument when applying a "requested" configuration to the instrument. If "current", the current configuration
            saved within the `~pyscope.telrun.Option` objects will be used. If "default", the default configuration set in each
            `~pyscope.telrun.Option` will be used.

        Returns
        -------
        `~pyscope.telrun.InstrumentConfiguration`
            The updated `~pyscope.telrun.InstrumentConfiguration` object with the new values from the
            `instrument_configuration` object.

        """
        logger.debug(
            """InstrumentConfiguration().__call__(
            instrument_configuration=%s,
            inherit_from=%s,
        )"""
            % (
                instrument_configuration,
                inherit_from,
            )
        )
