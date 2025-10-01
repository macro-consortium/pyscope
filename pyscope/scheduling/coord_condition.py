import logging

from .boundary_condition import BoundaryCondition

logger = logging.getLogger(__name__)


class CoordinateCondition:
    def __init__(
        self,
        coord_type="altaz",
        coord_idx=0,
        min_val=None,
        max_val=None,
        score_type="boolean",
        inclusive=True,
        ref_coord=None,
    ):
        """
        A restriction on the coordinates of the target viewed from a specific location
        and at a specific time.

        A manager to handle restrictions of a source's location when it is observered. The
        coordinates can be specified in right ascension and declination, galactic latitude
        and longitude, or altitude and azimuth.

        Parameters
        ----------
        coord_type : `str`, default : "altaz", {"altaz", "radec", "hourangle", "airmass"}
            The type of coordinate system to use. The options are "altaz" for altitude
            and azimuth, "radec" for right ascension and declination, and "hourangle" for
            hour angle. The default is "altaz".

        coord_idx : `int`, default : 0, {0, 1}
            The index of the coordinate to use. The default is 0 for the first coordinate. This
            parameter is ignored if `min_val` and `max_val` both contain two values for the
            minimum and maximum values of each coordinate.

        min_val : `~astropy.units.Quantity`, default : `None`
            The minimum value for the coordinate. If `None`, there is no minimum value.

        max_val : `~astropy.units.Quantity`, default : `None`
            The maximum value for the coordinate. If `None`, there is no maximum value.

        score_type : `str`, default : "boolean", {"linear", "boolean"}
            The type of scoring function to use. The options are "linear" for a linear
            function, commonly used for altitude, and "boolean" for a binary function
            that returns 1 if the condition is met and 0 if it is not, commonly used for
            determining if the source is above or below the horizon. The default is "boolean".

        inclusive : `bool`, default : `True`
            If `True`, the condition is inclusive, meaning that the target must be within
            the specified range. If `False`, the condition is exclusive, meaning that the
            target must be outside the specified range. Useful for excluding certain parts
            of the sky where a mount may be in jeopardy.

        ref_coord : `~astropy.coordinates.SkyCoord`, default : `None`
            If `coord_type` is "radec" or "galactic", a user can specify a center value
            and `min_val` and `max_val` will be interpreted as a minimum and maximum angular
            separation of the target from the reference coordinate.

        """
        logger.debug(
            """
            CoordinateCondition(
                coord_type=%s,
                coord_idx=%i,
                min_val=%s,
                max_val=%s,
                score_type=%s,
                inclusive=%s,
                ref_coord=%s,
            )"""
            % (
                coord_type,
                coord_idx,
                min_val,
                max_val,
                score_type,
                inclusive,
                ref_coord,
            )
        )

    @classmethod
    def from_string(
        self,
        string,
        coord_type=None,
        coord_idx=None,
        min_val=None,
        max_val=None,
        score_type=None,
        inclusive=None,
        ref_coord=None,
    ):
        """
        Create a `~pyscope.telrun.CoordinateCondition` or a `list` of `~pyscope.telrun.CoordinateCondition` objects from a `str`
        representation of a `~pyscope.telrun.CoordinateCondition`.
        All optional parameters are used to override the parameters extracted from the `str` representation.

        Parameters
        ----------
        string : `str`, required

        coord_type : `str`, default : `None`

        coord_idx : `int`, default : `None`

        min_val : `~astropy.units.Quantity`, default : `None`

        max_val : `~astropy.units.Quantity`, default : `None`

        score_type : `str`, default : `None`

        inclusive : `bool`, default : `None`

        ref_coord : `~astropy.coordinates.SkyCoord`, default : `None`

        """
        logger.debug(
            "CoordinateCondition.from_string(string=%s, coord_type=%s, coord_idx=%s, min_val=%s, max_val=%s, score_type=%s, inclusive=%s, ref_coord=%s)"
            % (
                string,
                coord_type,
                coord_idx,
                min_val,
                max_val,
                score_type,
                inclusive,
                ref_coord,
            )
        )

    def __str__(self):
        """
        Return a `str` representation of the `~pyscope.telrun.CoordinateCondition`.

        Returns
        -------
        `str`
            A `str` representation of the `~pyscope.telrun.CoordinateCondition`.

        """
        logger.debug("CoordinateCondition().__str__()")

    @staticmethod
    def _func(self, target, time, location):
        """
        Determine if the target meets the coordinate condition.

        Parameters
        ----------
        target : `~astropy.coordinates.SkyCoord`, required
            The target to check.

        time : `~astropy.time.Time`, required
            The time of the observation.

        location : `~astropy.coordinates.EarthLocation`, required
            The location of the observer.

        Returns
        -------
        `float` or `bool`
            The score value of the target. If `score_type` is "linear", the score is a `float`
            value between 0 and 1. If `score_type` is "boolean", the score is a `bool` value of
            `True` if the target meets the condition and `False` if it does not.

        """
        logger.debug(
            "CoordinateCondition()._func(target=%s, time=%s, location=%s)"
            % (target, time, location)
        )

    @staticmethod
    def _lqs_func(self, value):
        """
        Calculate the linear quality score for the coordinate value.

        Parameters
        ----------
        value : `float` or `bool`, required

        Returns
        -------
        `float`
            The linear quality score for the coordinate value.

        """
        logger.debug("CoordinateCondition._lqs_func(value=%s)" % value)

    @property
    def coord_type(self):
        """
        The type of coordinate system to use. Options are "altaz" for altitude and azimuth, "radec" for right ascension
        and declination, and "galactic" for galactic latitude and longitude.

        Returns
        -------
        `str`
            The type of coordinate system to use.

        """
        logger.debug(
            "CoordinateCondition().coord_type == %s" % self._coord_type
        )
        return self._coord_type

    @property
    def coord_idx(self):
        """
        The index of the coordinate to use. The default is 0 for the first coordinate, e.g. altitude or right ascension.

        Returns
        -------
        `int`
            The index of the coordinate to use.

        """
        logger.debug("CoordinateCondition().coord_idx == %i" % self._coord_idx)
        return self._coord_idx

    @property
    def min_val(self):
        """
        If `None`, there is no minimum value. Otherwise, the minimum value for the coordinate.

        Returns
        -------
        `~astropy.units.Quantity`
            The minimum value for the coordinate.

        """
        logger.debug("CoordinateCondition().min_val == %s" % self._min_val)
        return self._min_val

    @property
    def max_val(self):
        """
        If `None`, there is no maximum value. Otherwise, the maximum value for the coordinate.

        Returns
        -------
        `~astropy.units.Quantity`
            The maximum value for the coordinate.

        """
        logger.debug("CoordinateCondition().max_val == %s" % self._max_val)
        return self._max_val

    @property
    def score_type(self):
        """
        The type of scoring function to use. Options are "linear" for a linear function, commonly used for altitude,
        and "boolean" for a binary function that returns 1 if the condition is met and 0 if it is not.

        Returns
        -------
        `str`
            The type of scoring function to use.

        """
        logger.debug(
            "CoordinateCondition().score_type == %s" % self._score_type
        )
        return self._score_type

    @property
    def inclusive(self):
        """
        If `True`, the condition is inclusive, meaning that the target must be within the specified range. If `False`,
        the condition is exclusive, meaning that the target must be outside the specified range.
        Essentially acts as a "not" operator.

        Returns
        -------
        `bool`
            If the condition is inclusive or exclusive.

        """
        logger.debug("CoordinateCondition().inclusive == %s" % self._inclusive)
        return self._inclusive

    @property
    def ref_coord(self):
        """
        If `coord_type` is "radec" or "galactic", a user can specify a center value and `min_val` and `max_val` will be interpreted
        as a minimum and maximum radial angular separation of the target from the reference coordinate.

        Returns
        -------
        `~astropy.coordinates.SkyCoord`
            The reference coordinate.

        """
        logger.debug("CoordinateCondition().ref_coord == %s" % self._ref_coord)
        return self._ref_coord
