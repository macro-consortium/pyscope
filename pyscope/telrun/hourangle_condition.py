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

        """
        logger.debug(
            """HourAngleCondition(
                min_hour_angle=%s,
                max_hour_angle=%s,
                score_type=%s
            )"""
            % (min_hour_angle, max_hour_angle, score_type)
        )

    @classmethod
    def from_string(cls, string, min_hour_angle=None, max_hour_angle=None):
        """
        Create a new `~pyscope.telrun.HourAngleCondition` or a `list` of `~pyscope.telrun.HourAngleCondition`
        objects from a `str`. Any optional parameters are used to override the parameters extracted from the `str`.

        Parameters
        ----------
        string : `str`, required

        min_hour_angle : `~astropy.units.Quantity`, default : `None`

        max_hour_angle : `~astropy.units.Quantity`, default : `None`

        Returns
        -------
        `~pyscope.telrun.HourAngleCondition` or `list` of `~pyscope.telrun.HourAngleCondition`

        """
        logger.debug(
            "HourAngleCondition.from_string(string=%s, min_hour_angle=%s, max_hour_angle=%s)"
            % (string, min_hour_angle, max_hour_angle)
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

    def __repr__(self):
        """
        Return a `str` representation of the `~pyscope.telrun.HourAngleCondition`.

        Returns
        -------
        `str`
            A `str` representation of the `~pyscope.telrun.HourAngleCondition`.
        """
        logger.debug("HourAngleCondition().__repr__()")
        return str(self)

    def __call__(self, time, location, target):
        """
        Compute the score for the hour angle condition.

        Parameters
        ----------
        time : `~astropy.time.Time`, required
            The time at which the observation is to be made.

        location : `~astropy.coordinates.EarthLocation`, required
            The location of the observer.

        target : `~astropy.coordinates.SkyCoord`, required
            The target to evaluate the condition for.

        Returns
        -------
        `float`
            The score for the hour angle condition from `0` to `1`.

        """
        logger.debug(
            "HourAngleCondition().__call__(time=%s, location=%s, target=%s)"
            % (time, location, target)
        )

    def plot(self, time, location, target=None, ax=None):
        """ """
        pass
