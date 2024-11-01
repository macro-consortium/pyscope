import logging

from .boundary_condition import BoundaryCondition

logger = logging.getLogger(__name__)


class CoordinateCondition(BoundaryCondition):
    def __init__(
        self,
        coord_type="altaz",
        coord_idx=0,
        min_val=None,
        max_val=None,
        score_type="boolean",
        ref_coord=None,
        **kwargs,
    ):
        """
        A restriction on the coordinates of the target viewed from a specific location
        and at a specific time.

        A manager to handle restrictions of a source's location when it is observered. The
        coordinates can be specified in right ascension and declination, galactic latitude
        and longitude, or altitude and azimuth.

        Parameters
        ----------
        coord_type : `str`, default : "altaz", {"altaz", "radec", "galactic"}
            The type of coordinate system to use. The options are "altaz" for altitude
            and azimuth, "radec" for right ascension and declination, and "galactic" for
            galactic latitude and longitude. The default is "altaz".

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

        ref_coord : `~astropy.coordinates.SkyCoord`, default : `None`
            If `coord_type` is "radec" or "galactic", a user can specify a center value
            and `min_val` and `max_val` will be interpreted as a minimum and maximum angular
            separation of the target from the reference coordinate.

        **kwargs : `dict`, default : {}
            Additional keyword arguments to pass to the `~pyscope.telrun.BoundaryCondition` constructor.

        """
        logger.debug(
            """
            CoordinateCondition(
                coord_type=%s,
                coord_idx=%i,
                min_val=%s,
                max_val=%s,
                score_type=%s,
                ref_coord=%s,
                kwargs=%s
            )"""
            % (coord_type, coord_idx, min_val, max_val, score_type, ref_coord, kwargs)
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
        ref_coord=None,
        **kwargs,
    ):
        """
        Create a `~pyscope.telrun.CoordinateCondition` or a `list` of `~pyscope.telrun.CoordinateCondition` objects from a `str` representation of a `~pyscope.telrun.CoordinateCondition`.
        All optional parameters are used to override the parameters extracted from the `str` representation.

        Parameters
        ----------
        string : `str`, required

        coord_type : `str`, default : `None`

        coord_idx : `int`, default : `None`

        min_val : `~astropy.units.Quantity`, default : `None`

        max_val : `~astropy.units.Quantity`, default : `None`

        score_type : `str`, default : `None`

        ref_coord : `~astropy.coordinates.SkyCoord`, default : `None`

        **kwargs : `dict`, default : {}

        """
        logger.debug(
            "CoordinateCondition.from_string(string=%s, coord_type=%s, coord_idx=%s, min_val=%s, max_val=%s, score_type=%s, kwargs=%s)"
            % (string, coord_type, coord_idx, min_val, max_val, score_type, kwargs)
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
    def _func():
        pass

    @staticmethod
    def _lqs_func():
        pass

    @property
    def coord_type(self):
        pass

    @property
    def coord_idx(self):
        pass

    @property
    def min_val(self):
        pass

    @property
    def max_val(self):
        pass

    @property
    def score_type(self):
        pass

    @property
    def ref_coord(self):
        pass
