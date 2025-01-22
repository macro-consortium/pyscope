import logging
from pathlib import Path

from astropy import units as u

from ._field import _Field

logger = logging.getLogger(__name__)


class DarkField:
    @u.quantity_input(exp="s")
    def __init__(
        self,
        target=None,
        config=None,
        exp=0 * u.s,
        nexp=1,
        out_fname=Path(""),
        **kwargs,
    ):
        """
        A request to capture a dark frame.

        The basic class for collecting dark images. A `~pyscope.telrun.DarkField` is a `~pyscope.telrun.Field`
        that does not require a target and can set the exposure time and number of exposures, as well as the output filename.

        Parameters
        ----------
        target : `~astropy.coordinates.SkyCoord`, default : `None`
            The target field to observe. This is typically used to set a pointing that reduces
            the cross-section of the detector to the sky to minimize the number of cosmic rays
            that are captured in the dark frame. If `None`, the pointing will not change
            and the dark frame will be taken in the current position of the telescope.

        config : `~pyscope.telrun.InstrumentConfiguration`, default : `None`
            The instrument configuration to use for the observation. If None, the
            default configuration from the `~pyscope.telrun.ScheduleBlock` will be used.

        exp : `~astropy.units.Quantity`, default : 0 sec
            The length of the exposure in seconds.

        nexp : `int`, default : 1
            The number of exposures to take.

        out_fname : `~pathlib.Path` or `str`, default : Path("")
            The output filename for the observation. If not specified, the filename
            will be automatically generated.

        **kwargs : `dict`, default : {}
            Additional keyword arguments to pass to the instrument for the observation.

        """
        logger.debug(
            "DarkField(target=%s, config=%s, exp=%s, nexp=%i, out_fname=%s, kwargs=%s)"
            % (target, config, exp, nexp, out_fname, kwargs)
        )

    @classmethod
    @u.quantity_input(exp="s")
    def from_string(
        cls,
        string,
        target=None,
        config=None,
        exp=0 * u.s,
        nexp=1,
        out_fname=Path(""),
        **kwargs,
    ):
        """
        Create a `~pyscope.telrun.DarkField` or a `list` of `~pyscope.telrun.DarkField` objects from a `str` representation of a `~pyscope.telrun.DarkField`.
        All optional parameters are used to override the parameters extracted from the `str` representation.

        Parameters
        ----------
        string : `str`, required

        target : `~astropy.coordinates.SkyCoord`, default : `None`

        config : `~pyscope.telrun.Config`, default : `None`

        exp : `~astropy.units.Quantity`, default : 0 sec

        nexp : `int`, default : 1

        out_fname : `~pathlib.Path` or `str`, default : Path("")

        **kwargs : `dict`, default : {}

        """
        logger.debug(
            "DarkField.from_string(string=%s, target=%s, config=%s, exp=%s, nexp=%i, out_fname=%s, kwargs=%s)"
            % (string, target, config, exp, nexp, out_fname, kwargs)
        )

    def __str__(self):
        """
        Return a `str` representation of the `~pyscope.telrun.DarkField`.

        Returns
        -------
        `str`
        """
        pass

    @property
    def exp(self):
        """
        The exposure time for the dark frame.

        Returns
        -------
        `~astropy.units.Quantity`
        """
        return self._exp

    @exp.setter
    @u.quantity_input(value="sec")
    def exp(self, value):
        pass

    @property
    def nexp(self):
        """
        The number of exposures to take.

        Returns
        -------
        `int`
        """
        return self._nexp

    @nexp.setter
    def nexp(self, value):
        """
        Set the number of exposures to take.

        Parameters
        ----------
        value : `int`, required
        """
        pass

    @property
    def out_fname(self):
        """
        The output filename for the dark frame.

        Returns
        -------
        `~pathlib.Path`
        """
        return self._out_fname

    @out_fname.setter
    def out_fname(self, value):
        """
        Set the output filename for the dark frame.

        Parameters
        ----------
        value : `~pathlib.Path` or `str`, required
        """
        pass
