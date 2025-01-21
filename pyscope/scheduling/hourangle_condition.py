import logging

import astropy.units as u

from .boundary_condition import BoundaryCondition

logger = logging.getLogger(__name__)


class HourAngleCondition(BoundaryCondition):
    def __init__(
        self,
        min_hour_angle=-6 * u.hourangle,
        max_hour_angle=6 * u.hourangle,
        score_type="linear",
        inclusive=True,
    ):
        """
        A restriction on the hour angle over which a target can be observed.

        Contains a minimum and maximum hour angle, which are the hour angles at which the target is on the horizon
        by default. Stricter conditions can be set by changing these values. The hour angle is the angular distance
        along the celestial equator from the observer's meridian to the hour circle passing through the target.
        By default, the score varies linearly with the hour angle zeroing at the minimum and maximum hour angles
        and peaking at the meridian, however, this behavior can be changed by setting the `score_type` parameter.

        Parameters
        ----------
        min_hour_angle : `~astropy.units.Quantity`, default : -6*u.hourangle
            The minimum hour angle at which the target can be observed. The default is -6 hours (i.e., 6 hours
            times 15 degrees per hour = 90 degrees east of the meridian, or the horizon in the east).

        max_hour_angle : `~astropy.units.Quantity`, default : 6*u.hourangle
            The maximum hour angle at which the target can be observed. The default is 6 hours (i.e., 6 hours
            times 15 degrees per hour = 90 degrees west of the meridian, or the horizon in the west).

        score_type : `str`, default : "linear", {"linear", "boolean"}
            The type of scoring function to use. The options are "linear" for a linear function, commonly used
            for optimizing the observing time, and "boolean" for a binary function that returns 1 if the condition
            is met and 0 if it is not. The default is "linear".

        inclusive : `bool`, default : `True`
            If `True`, the condition is inclusive, meaning that the target must be within the specified range.
            If `False`, the condition is exclusive, meaning that the target must be outside the specified range.

        """
        logger.debug(
            """HourAngleCondition(
                min_hour_angle=%s,
                max_hour_angle=%s,
                score_type=%s,
                inclusive=%s
            )"""
            % (min_hour_angle, max_hour_angle, score_type, inclusive)
        )

    @classmethod
    def from_string(
        cls,
        string,
        min_hour_angle=None,
        max_hour_angle=None,
        score_type=None,
        inclusive=None,
    ):
        """
        Create a new `~pyscope.telrun.HourAngleCondition` or a `list` of `~pyscope.telrun.HourAngleCondition`
        objects from a `str`. Any optional parameters are used to override the parameters extracted from the `str`.

        Parameters
        ----------
        string : `str`, required

        min_hour_angle : `~astropy.units.Quantity`, default : `None`

        max_hour_angle : `~astropy.units.Quantity`, default : `None`

        score_type : `str`, default : `None`

        inclusive : `bool`, default : `None`

        Returns
        -------
        `~pyscope.telrun.HourAngleCondition` or `list` of `~pyscope.telrun.HourAngleCondition`

        """
        logger.debug(
            """HourAngleCondition.from_string(
                string=%s,
                min_hour_angle=%s,
                max_hour_angle=%s,
                score_type=%s,
                inclusive=%s
            )"""
            % (string, min_hour_angle, max_hour_angle, score_type, inclusive)
        )

    def __str__(self):
        """
        Return a `str` representation of the `~pyscope.telrun.HourAngleCondition`.

        Returns
        -------
        `str`
            A `str` representation of the `~pyscope.telrun.HourAngleCondition`.

        """
        logger.debug("HourAngleCondition().__str__()")

    @staticmethod
    def _func(self, target, time, location):
        """
        Calculate the hour angle value for the target.

        Parameters
        ----------
        target : `~astropy.coordinates.SkyCoord`, required
            The target to calculate the hour angle value for.

        time : `~astropy.time.Time`, required
            The time at which to calculate the hour angle value.

        location : `~astropy.coordinates.EarthLocation`, required
            The location at which to calculate the hour angle value.

        Returns
        -------
        `~astropy.units.Quantity`
            The hour angle value for the target.

        """
        logger.debug(
            "HourAngleCondition._func(target=%s, time=%s, location=%s)"
            % (target, time, location)
        )

    @staticmethod
    def _lqs_func(self, value):
        """
        Calculate the linear quality score for the hour angle value.

        Parameters
        ----------
        value : `~astropy.units.Quantity`, required
            The hour angle value for the target.

        Returns
        -------
        `float`
            The linear quality score for the hour angle value.

        """
        logger.debug("HourAngleCondition._lqs_func(value=%s)" % value)

    @property
    def min_hour_angle(self):
        """
        The minimum hour angle at which the target can be observed.

        Returns
        -------
        `~astropy.units.Quantity`
            The minimum hour angle at which the target can be observed

        """
        logger.debug(
            "HourAngleCondition().min_hour_angle == %s" % self._min_hour_angle
        )
        return self._min_hour_angle

    @property
    def max_hour_angle(self):
        """
        The maximum hour angle at which the target can be observed.

        Returns
        -------
        `~astropy.units.Quantity`
            The maximum hour angle at which the target can be observed

        """
        logger.debug(
            "HourAngleCondition().max_hour_angle == %s" % self._max_hour_angle
        )
        return self._max_hour_angle

    @property
    def score_type(self):
        """
        The type of scoring function to use. The options are "linear" for a linear function, commonly used for
        optimizing the observing time, and "boolean" for a binary function that returns 1 if the condition is met
        and 0 if it is not.

        Returns
        -------
        `str`
            The type of scoring function to use.

        """
        logger.debug(
            "HourAngleCondition().score_type == %s" % self._score_type
        )
        return self._score_type

    @property
    def inclusive(self):
        """
        If `True`, the condition is inclusive, meaning that the target must be within the specified range.
        If `False`, the condition is exclusive, meaning that the target must be outside the specified range.

        Returns
        -------
        `bool`
            If `True`, the condition is inclusive. If `False`, the condition is exclusive.

        """
        logger.debug("HourAngleCondition().inclusive == %s" % self._inclusive)
        return self._inclusive
