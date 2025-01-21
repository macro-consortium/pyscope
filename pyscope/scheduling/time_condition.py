import logging

from .boundary_condition import BoundaryCondition

logger = logging.getLogger(__name__)


class TimeCondition(BoundaryCondition):
    def __init__(
        self,
        time_type="local",  # local, utc, specified tz/location, or lst at location
        min_time=None,
        max_time=None,
        score_type="boolean",
        inclusive=True,
        ref_time=None,
    ):
        """
        A restriction on the time of an observation. The time can be specified
        several ways: local, UTC, a specified timezone, or LST at a location.

        Parameters
        ----------
        time_type : `str`, default : "local"
            The type of time to use. Can be "local", "utc", a timezone
            string or an `~astropy.coordinates.EarthLocation` for a timezone lookup, or "lst".

        min_time : `~astropy.time.Time`, default : `None`
            The minimum time for the observation.

        max_time : `~astropy.time.Time`, default : `None`
            The maximum time for the observation.

        score_type : `str`, default : "boolean"
            The type of score to return. Can be "boolean" or "linear". If "boolean",
            the score is `True` if the target meets the condition and `False` if it does not.
            If "linear", the score is a `float` value between 0 and 1.

        inclusive : `bool`, default : `True`
            Whether the min and max values are inclusive.

        ref_time : `~astropy.time.Time`, default : `None`
            The reference time to use for the condition. If specified, the `min_time` and
            `max_time` are relative to this time.

        """
        logger.debug(
            "TimeCondition.__init__(time_type=%s, min_time=%s, max_time=%s, score_type=%s, inclusive=%s, ref_time=%s)"
            % (time_type, min_time, max_time, score_type, inclusive, ref_time)
        )

    @classmethod
    def from_string(
        cls,
        string,
        time_type=None,
        min_time=None,
        max_time=None,
        score_type=None,
        inclusive=None,
        ref_time=None,
    ):
        """
        Create a `~pyscope.telrun.TimeCondition` or a `list` of `~pyscope.telrun.TimeCondition` objects
        from a `str` representation of a `~pyscope.telrun.TimeCondition`. All optional parameters are
        used to override the parameters extracted from the `str` representation.

        Parameters
        ----------
        string : `str`, required

        time_type : `str`, default : `None`

        min_time : `~astropy.time.Time`, default : `None`

        max_time : `~astropy.time.Time`, default : `None`

        score_type : `str`, default : `None`

        inclusive : `bool`, default : `None`

        ref_time : `~astropy.time.Time`, default : `None`

        """
        logger.debug(
            "TimeCondition.from_string(string=%s, time_type=%s, min_time=%s, max_time=%s, score_type=%s, inclusive=%s, ref_time=%s)"
            % (string, time_type, min_time, max_time, score_type, inclusive, ref_time)
        )

    def __str__(self):
        """
        Return a `str` representation of the `~pyscope.telrun.TimeCondition`.

        Returns
        -------
        `str`
            A `str` representation of the `~pyscope.telrun.TimeCondition`.

        """
        logger.debug("TimeCondition().__str__()")

    @staticmethod
    def _func(self, target, time, location):
        """
        Check if the target meets the time condition.

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
            The score for the time condition. If `score_type` is "boolean", the score is `True` if the target
            meets the condition and `False` if it does not. If `score_type` is "linear", the score is a `float`
            value between 0 and 1.

        """
        logger.debug(
            "TimeCondition()._func(target=%s, time=%s, location=%s)"
            % (target, time, location)
        )

    @staticmethod
    def _lqs_func(self, value):
        """
        Calculate the linear quality score for the score value.

        Parameters
        ----------
        value : `float`, required
            The score value for the target.

        Returns
        -------
        `float`
            The linear quality score for the score value.

        """
        logger.debug("TimeCondition()._lqs_func(value=%s)" % value)

    @property
    def min_time(self):
        """
        The minimum time for the observation.

        Returns
        -------
        `~astropy.time.Time`
            The minimum time for the observation.

        """
        logger.debug("TimeCondition().min_time == %s" % self._min_time)
        return self._min_time

    @property
    def max_time(self):
        """
        The maximum time for the observation.

        Returns
        -------
        `~astropy.time.Time`
            The maximum time for the observation.

        """
        logger.debug("TimeCondition().max_time == %s" % self._max_time)
        return self._max_time

    @property
    def time_type(self):
        """
        The type of time to use. Can be "local", "utc", a timezone string or an
        `~astropy.coordinates.EarthLocation` for a timezone lookup, or "lst".

        Returns
        -------
        `str`
            The type of time to use.

        """
        logger.debug("TimeCondition().time_type == %s" % self._time_type)
        return self._time_type

    @property
    def score_type(self):
        """
        The type of score to return. Can be "boolean" or "linear". If "boolean",
        the score is `True` if the target meets the condition and `False` if it does not.
        If "linear", the score is a `float` value between 0 and 1.

        Returns
        -------
        `str`
            The type of score to return.

        """
        logger.debug("TimeCondition().score_type == %s" % self._score_type)
        return self._score_type

    @property
    def inclusive(self):
        """
        Whether the min and max values are inclusive. Operates as a "not" on the
        condition. If `True`, the min and max values are inclusive. If `False`, the
        min and max values are exclusive.

        Returns
        -------
        `bool`
            Whether the min and max values are inclusive.

        """
        logger.debug("TimeCondition().inclusive == %s" % self._inclusive)
        return self._inclusive

    @property
    def ref_time(self):
        """
        The reference `~astropy.time.Time` to use for the condition. If specified, the `min_time` and
        `max_time` are relative to this time. A timezone specified in the `ref_time`
        `~astropy.time.Time` object will override the `time_type` parameter.

        Returns
        -------
        `~astropy.time.Time`
            The reference time to use for the condition.

        """
        logger.debug("TimeCondition().ref_time == %s" % self._ref_time)
        return self._ref_time
