import logging

import astropy.units as u

from .field import Field

logger = logging.getLogger(__name__)


class TransitionField(Field):
    @u.quantity_input(est_duration="s")
    def __init__(
        self,
        target=None,
        config=None,
        est_duration=0 * u.s,
        **kwargs,
    ):
        """
        Time for re-pointing and re-configuring the telescope between two fields.

        A `~pyscope.telrun.TransitionField` is a `~pyscope.telrun.Field` that represents a transition between two `~pyscope.telrun.Field` objects.
        These are typically only created by the `~pyscope.observatory.Observatory` when building the `~pyscope.telrun.ScheduleBlock` but can be manually
        requested to create a pause between two other `~pyscope.telrun.Field` objects.

        Parameters
        ----------
        target : `~astropy.coordinates.SkyCoord` or `None`, default : `None`
            The target field to point to during the transition. If `None`, the telescope will not move during the transition.

        config : `~pyscope.telrun.Configuration` or `None`, default : `None`
            The instrument configuration to use during the transition. If `None`, the configuration will not change during the transition.

        est_duration : `~astropy.units.Quantity`, default : 0 sec
            The duration of the transition in seconds. Typically, the `~pyscope.observatory.Observatory` will calculate the duration and set this value.

        **kwargs : dict, default : {}
            Additional keyword arguments to pass to the instrument for the observation

        """
        logger.debug(
            "TransitionField(target=%s, config=%s, duration=%s, kwargs=%s)"
            % (target, config, duration, kwargs)
        )

    @classmethod
    @u.quantity_input(est_duration="s")
    def from_string(
        cls,
        string,
        target=None,
        config=None,
        est_duration=0 * u.s,
        **kwargs,
    ):
        """
        Create a `~pyscope.telrun.TransitionField` or a `list` of `~pyscope.telrun.TransitionField` objects from a `str`
        representation of a `~pyscope.telrun.TransitionField`. All optional parameters are used to override the parameters
        extracted from the `str` representation.

        Parameters
        ----------
        string : `str`, required

        target : `~astropy.coordinates.SkyCoord` or `None`, default : `None`

        config : `~pyscope.telrun.Config` or `None`, default : `None`

        est_duration : `~astropy.units.Quantity`, default : 0 sec

        **kwargs : dict, default : {}

        Returns
        -------
        `~pyscope.telrun.TransitionField` or `list` of  ~pyscope.telrun.TransitionField`

        """
        logger.debug(
            "TransitionField.from_string(string=%s, target=%s, config=%s, kwargs=%s)"
            % (string, target, config, kwargs)
        )

    def __str__(self):
        """
        Return a `str` representation of the `~pyscope.telrun.TransitionField`.

        Returns
        -------
        `str`
            A `str` representation of the `~pyscope.telrun.TransitionField`.

        """
        logger.debug("TransitionField.__str__() == %s" % self)
