import logging
from pathlib import Path

from astropy import units as u

from .field import Field

logger = logging.getLogger(__name__)


class LightField(Field):
    @u.quantity_input(exp="s")
    def __init__(
        self,
        target,
        config=None,
        repositioning=None,
        dither=0 * u.arcsec,
        exp=0 * u.s,
        nexp=1,
        out_fname=Path(""),
        conditions=[],
        **kwargs
    ):
        """
        A single science target field and configuration for an observation.

        The `~pyscope.telrun.LightField` is the basic unit of a standard science observation. It contains the target, instrument
        `~pyscope.telrun.InstrumentConfiguration`, `~pyscope.observatory.Observatory.repositioning` offsets, exposure time, number of exposures,
        output filename `~pathlib.Path`, and scheduling `~pyscope.telrun.BoundaryCondition` objects. The `~pyscope.telrun.LightField`
        is used by the `~pyscope.telrun.Observer` to build a `~pyscope.telrun.ScheduleBlock` for a given observation request.

        Parameters
        ----------
        target : `~astropy.coordinates.SkyCoord` or `str`, required
            The target field to observe. If the target has proper motion, ensure
            that the reference epoch and the proper motions are set. If a string is
            passed, it will be converted to a `~astropy.coordinates.SkyCoord` object
            using the `astropy.coordinates.SkyCoord.from_name` method. If that fails,
            the class will attempt to resolve the target as an ephemeris object, first
            using the `astropy.coordinates.get_body` method and then the
            `astroquery.solarsystem.MPC.get_ephemeris()` method.

        config : `~pyscope.telrun.InstrumentConfiguration`, default : `None`
            The instrument configuration to use for the observation. If None, the
            default configuration from the `~pyscope.telrun.ScheduleBlock` will be used.

        repositioning : 2-`tuple` of `~astropy.units.Quantity`, default : `None`
            The position in pixels or arcseconds to reposition the telescope pointing
            relative to the target coordinates using the `~pyscope.observatory.Observatory.repositioning`
            method. The first element of the tuple is the x-axis offset in pixels or the right ascension
            offset in arcseconds, and the second element is the y-axis offset in pixels or the declination
            offset in arcseconds. If `None`, the telescope will not be reposition and the target will be observed
            after a "blind" slew to the target coordinates. Repositioning will only happen once at the start
            of the observation.

        dither : `~astropy.units.Quantity`, default : 0 arcsec
            The dither radius in arcseconds or pixels to use for each exposure. If the
            value is in arcseconds, the dither will be converted to pixels using the
            pixel scale of the `~pyscope.observatory.Observatory` configuration. A new
            dither position will be applied prior to each exposure.

        exp : `~astropy.units.Quantity`, default : 0 sec
            The length of the exposure in seconds.

        nexp : `int`, default : 1
            The number of exposures to take.

        out_fname : `~pathlib.Path` or `str`, default : Path("")
            The output filename for the observation. If not specified, the filename
            will be automatically generated.

        conditions : `list` of `~pyscope.telrun.BoundaryCondition`, default : []
            A list of `~pyscope.telrun.BoundaryCondition` objects that define the scheduling
            constraints for this field. The `~pyscope.telrun.Optimizer` inside the `~pyscope.telrun.Scheduler`
            will use the `~pyscope.telrun.BoundaryCondition` objects to determine the best possible schedule.

        **kwargs : `dict`, default : {}
            Additional keyword arguments to pass to the instrument for the observation.

        """
        logger.debug(
            "LightField(target=%s, config=%s, repositioning=%s, dither=%s, exp=%s, nexp=%i, out_fname=%s, conditions=%s, kwargs=%s)"
            % (
                target,
                config,
                repositioning,
                dither,
                exp,
                nexp,
                out_fname,
                conditions,
                kwargs,
            )
        )

        out_fname = Path(out_fname)

    @classmethod
    @u.quantity_input(exp="s")
    def from_string(
        cls,
        string,
        target=None,
        config=None,
        repositioning=None,
        dither=0 * u.arcsec,
        exp=0 * u.s,
        nexp=1,
        out_fname=Path(""),
        conditions=[],
        **kwargs
    ):
        """
        Create a `~pyscope.telrun.LightField` or a `list` of `~pyscope.telrun.LightField` objects from a `str` representation of a `~pyscope.telrun.LightField`.
        All non-required parameters are used to override the values in the `str` representation.

        Parameters
        ----------
        string : `str`, required

        target : `~astropy.coordinates.SkyCoord` or `str`, default : `None`

        config : `~pyscope.telrun.Config`, default : `None`

        repositioning : 2-`tuple` of `~astropy.units.Quantity`, default : `None`

        dither : `~astropy.units.Quantity`, default : 0 arcsec

        exp : `~astropy.units.Quantity`, default : 0 sec

        nexp : `int`, default : 1

        out_fname : `~pathlib.Path` or `str`, default : Path("")

        conditions : `list` of `~pyscope.telrun.BoundaryCondition`, default : []

        kwargs : `dict`, default : {}

        Returns
        -------
        `~pyscope.telrun.LightField` or `list` of `~pyscope.telrun.LightField`

        """
        logger.debug(
            "LightField.from_string(string=%s, target=%s, config=%s, repositioning=%s, dither=%s, exp=%s, nexp=%i, out_fname=%s, conditions=%s, kwargs=%s)"
            % (
                string,
                target,
                config,
                repositioning,
                dither,
                exp,
                nexp,
                out_fname,
                conditions,
                kwargs,
            )
        )

    def __str__(self):
        """
        Return a `str` representation of the `~pyscope.telrun.LightField`.

        Returns
        -------
        `str`
            A `str` representation of the `~pyscope.telrun.LightField`.

        """
        logger.debug("LightField().__str__() = %s" % self)

    @property
    def repositioning(self):
        """
        The pointing offset to reposition the telescope relative to the target coordinates.

        The position in detector pixels or arcseconds on the sky to reposition the telescope pointing
        relative to the provided target coordinates using the `~pyscope.observatory.Observatory.repositioning`
        method. The first element of the `tuple` is the x-axis offset in pixels or the right ascension
        offset in arcseconds, and the second element is the y-axis offset in pixels or the declination
        offset in arcseconds. If `None`, the telescope will not be repositioned and the target will be observed
        after a so-called "blind" slew to the target coordinates.

        Returns
        -------
        2-`tuple` of `~astropy.units.Quantity` or `None`
            The position in pixels or arcseconds to reposition the telescope pointing
            relative to the target coordinates.

        """
        logger.debug("LightField().repositioning == %s" % self._repositioning)
        return self._repositioning

    @repositioning.setter
    def repositioning(self, value):
        """
        Set the pointing offset to reposition the telescope relative to the target coordinates.

        Parameters
        ----------
        value : 2-`tuple` of `~astropy.units.Quantity` or `None`, required
            The position in pixels or arcseconds to reposition the telescope pointing
            relative to the target coordinates.

        """
        logger.debug("LightField().repositioning = %s" % value)

    @property
    def exp(self):
        """
        The length of the exposure in seconds.

        Returns
        -------
        `~astropy.units.Quantity`
            The length of the exposure in seconds.

        """
        logger.debug("LightField().exp == %s" % self._exp)
        return self._exp

    @exp.setter
    @u.quantity_input(exp="sec")
    def exp(self, value):
        """
        Set the length of the exposure in seconds.

        Parameters
        ----------
        value : `~astropy.units.Quantity`, required
            The length of the exposure in seconds.

        """
        logger.debug("LightField().exp = %s" % value)
        pass

    @property
    def nexp(self):
        """
        The number of exposures to take of this target field with the given `~pyscope.telrun.InstrumentConfiguration`.

        Returns
        -------
        `int`
            The number of exposures to take of this target field with the given `~pyscope.telrun.InstrumentConfiguration`.

        """
        logger.debug("LightField().nexp == %i" % self._nexp)
        return self._nexp

    @nexp.setter
    def nexp(self, value):
        """
        Set the number of exposures to take of this target field with the given `~pyscope.telrun.InstrumentConfiguration`.

        Parameters
        ----------
        value : `int`, required
            The number of exposures to take of this target field with the given `~pyscope.telrun.InstrumentConfiguration`.

        """
        logger.debug("LightField().nexp = %i" % value)
        pass

    @property
    def out_fname(self):
        """
        The output filename for the observation as a `~pathlib.Path`.

        Returns
        -------
        `~pathlib.Path`
            The output filename for the observation.

        """
        logger.debug("LightField().out_fname == %s" % self._out_fname)
        return self._out_fname

    @out_fname.setter
    def out_fname(self, value):
        """
        Set the output filename for the observation. The filename should be compatible with the `~pathlib.Path` class.

        Parameters
        ----------
        value : `~pathlib.Path` or `str`, required
            The output filename for the observation.

        """
        logger.debug("LightField().out_fname = %s" % value)
        pass

    @property
    def conditions(self):
        """
        The scheduling `~pyscope.telrun.BoundaryCondition` objects for this field. These constraints are used by
        the `~pyscope.telrun.Optimizer` to determine the best possible schedule for the
        `~pyscope.telrun.ScheduleBlock` containing this `~pyscope.telrun.LightField`.

        Returns
        -------
        `list` of `~pyscope.telrun.BoundaryCondition`
            A `list` of `~pyscope.telrun.BoundaryCondition` objects that define the scheduling
            constraints for this `~pyscope.telrun.LightField`.

        """
        logger.debug("LightField().conditions == %s" % self._conditions)
        return self._conditions

    @conditions.setter
    def conditions(self, value):
        """
        Set the scheduling `~pyscope.telrun.BoundaryCondition` objects for this field. These constraints are used by
        the `~pyscope.telrun.Optimizer` to determine the best possible schedule for the
        `~pyscope.telrun.ScheduleBlock` containing this `~pyscope.telrun.LightField`.

        Parameters
        ----------
        value : `list` of `~pyscope.telrun.BoundaryCondition`, required
            A `list` of `~pyscope.telrun.BoundaryCondition` objects that define the scheduling
            constraints for this `~pyscope.telrun.LightField`.

        """
        logger.debug("LightField().conditions = %s" % value)
        pass
