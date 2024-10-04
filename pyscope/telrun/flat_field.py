import logging
from pathlib import Path

from astropy import units as u

from .light_field import LightField

logger = logging.getLogger(__name__)


class FlatField(LightField):
    @u.quantity_input(exp="s")
    def __init__(
        self,
        target="CoverCalibrator",
        config=None,
        dither=0 * u.arcsec,
        exp=1 * u.s,
        nexp=1,
        auto_exp=0,
        out_fname=Path(""),
        conditions=[],
        **kwargs,
    ):
        """
        A request to take flat field images.

        The `~pyscope.telrun.FlatField` class is a subclass of the `~pyscope.telrun.LightField` class
        and supports several small differences specific to flat field imaging. First, the default target
        is the `CoverCalibrator` which will point the telescope at a pre-configured location to take flat
        field images. A user may change the target to any other valid `~astropy.coordinates.SkyCoord` for
        taking sky flats. Some `CoverCalibrator` instruments may support the ability to adjust their
        illumination level, and a user can change this by passing a `~pyscope.telrun.InstrumentConfiguration` with the
        appropriate settings.

        A user taking sky flats may want to take advantage of the `auto_exp` feature
        to automatically adjust the exposure time to a high SNR but not saturate the detector. The `dither`
        parameter can be used to move the telescope pointing slightly between exposures to help correct for
        bad pixels, the flat field illumination pattern of the `CoverCalibrator`, or to help with star
        rejection in sky flats.

        It is typically advantageous to schedule flat fields in a separate `~pyscope.telrun.ScheduleBlock`
        from science fields since the observing `~pyscope.telrun.BoundaryCondition` selections are often quite different.

        Parameters
        ----------
        target : `~astropy.coordinates.SkyCoord` or `str`, default : "CoverCalibrator"
            The target field to observe. If the target has proper motion, ensure
            that the reference epoch and the proper motions are set. The default is the
            `CoverCalibrator` which is a pre-configured location to take flat field images.

        config : `~pyscope.telrun.InstrumentConfiguration`, default : None
            The instrument configuration to use for the observation. If None, the
            default configuration from the `~pyscope.telrun.ScheduleBlock` will be used.

        dither : `~astropy.units.Quantity`, default : 0 arcsec
            The dither radius in arcseconds or pixels to use for each exposure. If the
            value is in arcseconds, the dither will be converted to pixels using the
            pixel scale of the `~pyscope.observatory.Observatory` configuration. A new
            dither position will be applied prior to each exposure.

        exp : `~astropy.units.Quantity`, default : 1 sec
            The exposure time for each exposure.

        nexp : `int`, default : 1
            The number of exposures to take.

        auto_exp : `int`, default : 0
            The number of counts to aim for in each exposure. If 0, the exposure time will
            not be adjusted. If the value is greater than 0, the exposure time will be adjusted
            to reach the target counts.

        out_fname : `~pathlib.Path` or `str`, default : Path("")
            The output filename for the flat field images. If the path is empty, the filenames
            will be generated automatically.

        conditions : `list` of `~pyscope.telrun.BoundaryCondition`, default : []
            A `list` of observing conditions that must be satisfied to schedule the flat fields.

        **kwargs : `dict`, default : {}
            Additional keyword arguments to pass to the instrument for the flat fields.

        """
        logger.debug(
            "FlatField(target=%s, config=%s, dither=%s, exp=%s, nexp=%i, auto_exp=%s, out_fname=%s, conditions=%s, kwargs=%s)"
            % (
                target,
                config,
                dither,
                exp,
                nexp,
                auto_exp,
                out_fname,
                conditions,
                kwargs,
            )
        )

    @classmethod
    @u.quantity_input(exp="s")
    def from_string(
        self,
        string,
        target=None,
        config=None,
        dither=0 * u.arcsec,
        exp=1 * u.s,
        nexp=1,
        auto_exp=0,
        out_fname=Path(""),
        conditions=[],
        **kwargs,
    ):
        """
        Create a `~pyscope.telrun.FlatField` or a `list` of `~pyscope.telrun.FlatField` objects from a `str` representation of a `~pyscope.telrun.FlatField`.
        All optional parameters are used to override the parameters extracted from the `str` representation.

        Parameters
        ----------
        string : `str`, required

        target : `~astropy.coordinates.SkyCoord`, default : None

        config : `~pyscope.telrun.Config`, default : None

        dither : `~astropy.units.Quantity`, default : 0 arcsec

        exp : `~astropy.units.Quantity`, default : 1 sec

        nexp : `int`, default : 1

        auto_exp : `int`, default : 0

        out_fname : `pathlib.Path`, default : Path("")

        conditions : `list` of `~pyscope.telrun.BoundaryCondition`, default : []

        **kwargs : `dict`, default : {}

        """
        logger.debug(
            "FlatField.from_string(string=%s, target=%s, config=%s, dither=%s, exp=%s, nexp=%i, auto_exp=%s, out_fname=%s, conditions=%s, kwargs=%s)"
            % (
                string,
                target,
                config,
                dither,
                exp,
                nexp,
                auto_exp,
                out_fname,
                conditions,
                kwargs,
            )
        )

    def __str__(self):
        """
        Return a `str` representation of the `~pyscope.telrun.FlatField`.

        Returns
        -------
        `str`
        """
        logger.debug("FlatField().__str__() = %s" % self)

    @property
    def auto_exp(self):
        """
        The number of counts to aim for in each exposure. If 0, the exposure time will
        not be adjusted. If the value is greater than 0, the exposure time will be adjusted
        to reach the target counts.

        Returns
        -------
        `int`
        """
        logger.debug("FlatField().auto_exp == %s" % self._auto_exp)
        return self._auto_exp

    @auto_exp.setter
    def auto_exp(self, value):
        """
        Set the number of counts to aim for in each exposure. If 0, the exposure time will
        not be adjusted. If the value is greater than 0, the exposure time will be adjusted
        to reach the target counts.

        Parameters
        ----------
        value : `int`, required
        """
        logger.debug("FlatField().auto_exp = %s" % value)
        pass
