import logging

from .boundary_condition import BoundaryCondition

logger = logging.getLogger(__name__)


class AirmassCondition(BoundaryCondition):
    def __init__(self, airmass_limit=3, formula="Schoenberg1929", weight=1):
        """
        A condition that penalizes targets for higher airmass values up to a limit.

        This condition is used to restrict the airmass value of a target to a maximum value. The airmass
        can be calculated using several different formulae. The most simple is a secant formula,
        given by :math:`X = \\frac{1}{\\cos(z)}` where :math:`z` is the angle between the target and the zenith. This is the
        analytic solution for a plane-parallel atmosphere.

        The default option is Schoenberg 1929[1]_, a geometric model for a non-refracting spherical atmosphere:

        .. math::
            X = \\frac{R_{\\oplus}}{y_{\\rm atm}}\\sqrt{\\cos^2(z) + 2\\frac{y_{\\rm atm}}{R_{\\oplus}} + \\left(\\frac{y_{\\rm atm}}{R_{\\oplus}}\\right)^2} - \\frac{R_{\\oplus}}{y_{\\rm atm}}\\cos(z)

        where :math:`R_{\\oplus} = 6371` km is the mean radius of the Earth and :math:`y_{\\rm atm} = \\frac{kT_0}{mg}` is the scale height of the atmosphere. For typical
        values, the scale height is 8435 m. For this value, the airmass at the horizon is :math:`\\approx 38.87`.

        The class also supports several basic interpolative models for the airmass. We list these below:

        - Young & Irvine 1967[2]_: :math:`X = \\sec(z_t)\\left[1 - 0.0012(\\sec^2z_t - 1)\\right]` where :math:`z_t` is the "true" zenith angle. Note that this formula becomes zero at :math:`z_t \\approx 88^{\\circ}`.

        - Hardie 1962[3]_: :math:`X = \\sec(z) - 0.0018167(\\sec(z) - 1) - 0.002875(\\sec(z) - 1)^2 - 0.0008083(\\sec(z) - 1)^3` where :math:`z` is the zenith angle. This formula approaches negative infinity at the horizon and is typically used for up to :math:`z \\approx 85^{\\circ}`.

        - Rozenberg 1966[4]_: :math:`X = (\\cos z + 0.025\\exp(-11\\cos z))^{-1}`. The horizon airmass is :math:`\\approx 40`.

        - Kasten & Young 1989[5]_: :math:`X = \\frac{1}{\\cos z + 0.50572(96.07995^{\\circ} - \\left[z\\right]_{\\rm degrees})^{-1.6364}}`. The horizon airmass is :math:`\\approx 38.7`. Note the :math:`\\left[z\\right]_{\\rm degrees}` is the zenith angle in degrees but the :math:`\\cos z` is in radians as usual.

        - Young 1994[6]_: :math:`X = \\frac{1.002432\\cos^2z_t + 0.148386\\cos z_t + 0.0096467}{\\cos^3z_t + 0.149864\\cos^2z_t + 0.0102963\\cos z_t + 0.000303978}`

        - Pickering 2002[7]_: :math:`X = \\frac{1}{\\sin((90^{\\circ} - \\left[z\\right]_{\\rm degrees}) + 244/(165 + 47(90^{\\circ} - \\left[z\\right]_{\\rm degrees})^{1.1}))}`


        These are all nicely discussed in the `Wikipedia article on Airmass <https://en.wikipedia.org/wiki/Air_mass_(astronomy)#Plane-parallel_atmosphere>`_, including this
        figure that shows the airmass as a function of zenith angle for the different models:

        .. image:: https://upload.wikimedia.org/wikipedia/commons/d/d3/Viewing_angle_and_air_masses.svg

        The airmass is penalized linearly from `1` with the best linear quality score and decreases to `0` at the `airmass_limit` and beyond.

        Parameters
        ----------
        airmass_limit : `float`, default : 3
            The maximum airmass value that is allowed.

        formula : `str`, default : "secant", {"secant", "Schoenberg1929", "Young+Irvine1967", "Hardie1962", "Rozenberg1966", "KastenYoung1989", "Young1994", "Pickering2002"}
            The formula to use to calculate the airmass value.

        weight : `float`, default : 1
            The weight of the condition in the final score. The default is 1.

        References
        ----------
        .. [1] `Schoenberg, E. 1929. Theoretische Photometrie, Über die Extinktion des Lichtes in der Erdatmosphäre. In Handbuch der Astrophysik. Band II, erste Hälfte. Berlin: Springer. <https://ia904707.us.archive.org/25/items/in.ernet.dli.2015.377128/2015.377128.Handbuch-Der.pdf>`_

        .. [2] `Young & Irvine 1967 <https://ui.adsabs.harvard.edu/abs/1967AJ.....72..945Y/abstract>`_

        .. [3] `Hardie 1962 <https://ui.adsabs.harvard.edu/abs/1962aste.book.....H/abstract>`_

        .. [4] `Rozenberg 1966 <https://search.worldcat.org/title/1066196615>`_

        .. [5] `Kasten & Young 1989 <https://ui.adsabs.harvard.edu/abs/1989ApOpt..28.4735K/abstract>`_

        .. [6] `Young 1994 <https://ui.adsabs.harvard.edu/abs/1994ApOpt..33.1108Y/abstract>`_

        .. [7] `Pickering 2002 <http://www.dioi.org/vols/wc0.pdf>`_

        """
        logger.debug("AirmassCondition(airmass_limit=%s, formula=%s, weight=%s)")
        super().__init__(func=self._func, lqs_func=self._lqs_func)

    @classmethod
    def from_string(self, string, airmass_limit=None, formula=None, weight=None):
        """
        Create a `~pyscope.telrun.AirmassCondition` or a `list` of `~pyscope.telrun.AirmassCondition` objects from a `str` representation of a `~pyscope.telrun.AirmassCondition`.
        Any optional parameters are used to override the parameters extracted from the `str` representation.

        Parameters
        ----------
        string : `str`, required

        airmass_limit : `float`, default : `None`

        formula : `str`, default : `None`

        weight : `float`, default : `None`

        """
        logger.debug(
            "AirmassCondition.from_string(string=%s, airmass_limit=%s, formula=%s, weight=%s)"
            % (string, airmass_limit, formula, weight)
        )

    def __str__(self):
        """
        Return a `str` representation of the `~pyscope.telrun.AirmassCondition`.

        Returns
        -------
        `str`
            A `str` representation of the `~pyscope.telrun.AirmassCondition`.

        """
        logger.debug("AirmassCondition().__str__()")

    @staticmethod
    def _func(target, time, location, formula="Schoenberg1929"):
        """
        Calculate the airmass value for the target.

        Parameters
        ----------
        target : `~astropy.coordinates.SkyCoord`, required
            The target to calculate the airmass value for.

        Returns
        -------
        `float`
            The airmass value for the target.

        """
        logger.debug("AirmassCondition._func(target=%s)" % target)

    @staticmethod
    def _lqs_func(self, value, airmass_limit=3):
        """
        Calculate the linear quality score for the airmass value.

        Parameters
        ----------
        value : `float`, required
            The airmass value for the target.

        airmass_limit : `float`, default : 3
            The maximum airmass value that is allowed.

        Returns
        -------
        `float`
            The linear quality score for the airmass value.

        """
        logger.debug(
            "AirmassCondition._lqs_func(value=%s, max_val=%s)" % (value, max_val)
        )

    @property
    def airmass_limit(self):
        """
        The maximum airmass value that is allowed.

        Returns
        -------
        `float`
            The maximum airmass value that is allowed.

        """
        logger.debug("AirmassCondition().airmass_limit == %s" % self._airmass_limit)
        return self._airmass_limit

    @property
    def formula(self):
        """
        The formula to use to calculate the airmass value.

        Returns
        -------
        `str`
            The formula to use to calculate the airmass value.

        """
        logger.debug("AirmassCondition().formula == %s" % self._formula)
        return self._formula
