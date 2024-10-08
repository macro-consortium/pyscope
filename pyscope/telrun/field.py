import logging
from uuid import uuid4

from astropy import units as u

logger = logging.getLogger(__name__)


class Field:
    def __init__(self, target, config=None, **kwargs):
        """
        A single target field and configuration for an observation.

        The `~pyscope.telrun.Field` is the basic unit of an observation. It contains
        the target, instrument configuration, exposure time, number of exposures, and
        output filename.

        Parameters
        ----------
        target : `~astropy.coordinates.SkyCoord`, required
            The target field to observe. If the target has proper motion, ensure
            that the reference epoch and the proper motions are set.

        config : `~pyscope.telrun.InstrumentConfiguration`, default : None
            The instrument configuration to use for the observation. If None, the
            default configuration from the `~pyscope.telrun.ScheduleBlock` will be used.

        **kwargs : dict, default : {}
            Additional keyword arguments to pass to the instrument for the observation.

        """
        logger.debug(
            "Field(target=%s, config=%s, exp=%i, nexp=%i, out_fname=%s, kwargs=%s)"
            % (target, config, exp, nexp, out_fname, kwargs)
        )

        self.target = target
        self.config = config
        self.kwargs = kwargs
        self._uuid = uuid4()
        self._est_duration = 0 * u.sec
        self._exec_status = "Unscheduled"
        self._exec_start = None
        self._exec_end = None
        self._exec_log = None
        logger.debug("Field() = %s" % self)

    @classmethod
    def from_string(cls, string, target=None, config=None, **kwargs):
        """
        Create a `~pyscope.telrun.Field` or a `list` of `~pyscope.telrun.Field` objects from a `str` representation of a `~pyscope.telrun.Field`.

        Parameters
        ----------
        string : `str`, required

        Returns
        -------
        `~pyscope.telrun.Field` or `list` of `~pyscope.telrun.Field`

        """
        logger.debug(
            "Field.from_string(string=%s, target=%s, config=%s, kwargs=%s)"
            % (string, target, config, kwargs)
        )

        logger.debug("Field.from_string() = %s" % field)

    def __str__(self):
        """
        Return a `str` representation of the `~pyscope.telrun.Field`.

        Returns
        -------
        `str`
            A `str` representation of the `~pyscope.telrun.Field`.

        """
        logger.debug("Field().__str__() = %s" % self)

    def __repr__(self):
        """
        Return a `str` representation of the `~pyscope.telrun.Field`.

        Returns
        -------
        `str`
            A `str` representation of the `~pyscope.telrun.Field`.

        """
        return str(self)

    @property
    def target(self):
        """
        The target field to observe.

        Returns
        -------
        `astropy.coordinates.SkyCoord`
            The target field to observe. If the target has proper motion, ensure
            that the reference epoch and the proper motions are set.

        """
        logger.debug("Field().target == %s" % self._target)
        return self._pointing

    @target.setter
    def target(self, value):
        """
        Set the target field to observe.

        Parameters
        ----------
        value : `~astropy.coordinates.SkyCoord`, required
            The target field to observe. If the target has proper motion, ensure
            that the reference epoch and the proper motions are set.

        """
        logger.debug("Field.target = %s" % value)
        pass

    @property
    def config(self):
        """
        The instrument `~pyscope.telrun.InstrumentConfiguration` to use for the `~pyscope.telrun.Field`.

        Returns
        -------
        `~pyscope.telrun.InstrumentConfiguration`
            The instrument `~pyscope.telrun.InstrumentConfiguration` to use for the `~pyscope.telrun.Field`.

        """
        logger.debug("Field().config == %s" % self._config)
        return self._config

    @config.setter
    def config(self, value):
        """
        Set the instrument `~pyscope.telrun.InstrumentConfiguration` to use for the `~pyscope.telrun.Field`.

        Parameters
        ----------
        value : `~pyscope.telrun.InstrumentConfiguration`, required
            The instrument `~pyscope.telrun.InstrumentConfiguration` to use for the `~pyscope.telrun.Field`.

        """
        logger.debug("Field().config = %s" % value)
        pass

    @property
    def kwargs(self):
        """
        Additional keyword arguments to pass to the instrument.

        Returns
        -------
        `dict`
            Additional keyword arguments to pass to the instrument.

        """
        logger.debug("Field().kwargs == %s" % self._kwargs)
        return self._kwargs

    @kwargs.setter
    def kwargs(self, value):
        """
        Set additional keyword arguments to pass to the instrument.

        Parameters
        ----------
        value : `dict`, required
            Additional keyword arguments to pass to the instrument.

        """
        logger.debug("Field().kwargs = %s" % value)
        pass

    @property
    def ID(self):
        """
        The unique identifier for the `~pyscope.telrun.Field`.

        Returns
        -------
        `uuid.UUID`
            The unique identifier for the `~pyscope.telrun.Field`.

        """
        logger.debug("Field().ID == %s" % self._uuid)
        return self._uuid

    @property
    def est_duration(self):
        """
        The estimated duration of the observation. This is estimated based on the
        properties of the target, the instrument configuration, and the observing
        conditions by the `~pyscope.observatory.Observatory`.

        Returns
        -------
        `~astropy.units.Quantity`
            The estimated duration of the observation.

        """
        logger.debug("Field().est_duration == %s" % self._est_duration)
        return self._est_duration

    @property
    def exec_status(self):
        """
        The execution status of the observation. The status is used to track the
        progress of the observation through the observation process. The status
        can be one of the following:
        - "_U_nscheduled"
        - "_E_xpired"
        - "_I_nvalid"
        - "_B_uilt"
        - "_Q_ueued"
        - "_S_cheduled"
        - "_W_aiting"
        - "_A_borted"
        - "_R_unning"
        - "_F_ailed"
        - "_P_artially Completed"
        - "_C_ompleted"
        These are all also uniquely specified by their first letter as a shorthand.

        Returns
        -------
        `str`
            The execution status of the observation.

        """
        logger.debug("Field().exec_status == %s" % self._exec_status)
        return self._exec_status

    @property
    def exec_start(self):
        """
        The actual execution start time of the observation. This is set by the
        `~pyscope.telrun.TelrunOperator` when the observation begins.

        Returns
        -------
        `~astropy.time.Time`
            The actual execution start time of the observation.

        """
        logger.debug("Field().exec_start == %s" % self._exec_start)
        return self._exec_start

    @property
    def exec_end(self):
        """
        The actual execution end time of the observation. This is set by the
        `~pyscope.telrun.TelrunOperator` when the observation ends.

        Returns
        -------
        `~astropy.time.Time`
            The actual execution end time of the observation.

        """
        logger.debug("Field().exec_end == %s" % self._exec_end)
        return self._exec_end

    @property
    def exec_log(self):
        """
        The execution log of the observation. This is a list of `str` messages
        that are generated by the `~pyscope.telrun.TelrunOperator` instance during
        the execution of the observation. The log is used to track the progress
        of the observation and to diagnose any issues in the resulting data that
        may have occurred during the observation. The log is generated using the
        Python `logging` module, see the `~pyscope.telrun.TelrunOperator` and the
        `logging` module documentation for more information.

        Returns
        -------
        `list` of `str`
            The execution log of the observation recorded using the Python `logging` module.

        """
        logger.debug("Field().exec_log == %s" % self._exec_log)
        return self._exec_log
