import logging
from pathlib import Path

from astropy import units as u

from .light_field import LightField

logger = logging.getLogger(__name__)


class AutofocusField(LightField):
    @u.quantity_input(exp="s", timeout="s")
    def __init__(
        self,
        target=None,
        config=None,
        repositioning=None,
        dither=0 * u.arcsec,
        exp=0 * u.s,
        nexp=1,
        midpoint=0,
        nsteps=7,
        stepsize=200,
        timeout=180 * u.s,
        out_fname=Path(""),
        conditions=[],
        **kwargs,
    ):
        """
        A request to complete an autofocus sequence on a target field.

        The `~pyscope.telrun.AutofocusField` is a special type of `~pyscope.telrun.LightField` that
        contains options to override the default autofocus parameters. The target field
        can be set to None to run the autofocus sequence on whatever target field the telescope
        is currently tracking. The autofocus sequence will be run at the midpoint of the
        exposure sequence with the specified number of steps and step size. At each step,
        the telescope will move the focus position by the step size and take `nexp` exposures
        of `exp` duration. The autofocus sequence will timeout after `timeout` seconds if the
        sequence is not completed.

        Parameters
        ----------
        target : `~astropy.coordinates.SkyCoord`, default : `None`
            The target field to autofocus on. If `None`, the telescope will autofocus on the
            current target field.

        config : `~pyscope.telrun.InstrumentConfiguration`, default : `None`
            The instrument configuration to use for the autofocus sequence. If `None`, the
            default configuration from the `~pyscope.telrun.ScheduleBlock` will be used.

        repositioning : 2-tuple of `~astropy.units.Quantity`, default : `None`
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

        exp : `~astropy.units.Quantity`, default : 5 sec
            The exposure time for each autofocus step.

        nexp : `int`, default : 1
            The number of exposures to take at each autofocus step. Multiple exposures can be used to
            smooth over rapid seeing variations.

        midpoint : `int`, default : 0
            The absolute step number at which to center the autofocus sequence. If 0, the autofocus
            sequence will occur at the current step number.

        nsteps : `int`, default : 7
            The number of autofocus steps to take. The total number of exposures will be `nexp * nsteps`.

        stepsize : `int`, default : 200
            The number of steps to move the focus position at each autofocus step.

        timeout : `~astropy.units.Quantity`, default : 180 sec
            The maximum time to wait for the autofocus sequence to complete before timing out.

        out_fname : `pathlib.Path`, default : Path("")
            The output filename for the autofocus sequence. If an empty `str`, the images will not be saved.

        conditions : `list` of `~pyscope.telrun.BoundaryCondition`, default : []
            A `list` of observing conditions that must be satisfied to schedule the autofocus sequence.

        **kwargs : `dict`, default : {}
            Additional keyword arguments to pass to the instrument for the autofocus sequence.

        """
        logger.debug(
            "AutofocusField(target=%s, config=%s, repositioning=%s, dither=%s, exp=%s, nexp=%i, midpoint=%i, nsteps=%i, stepsize=%i, timeout=%s, out_fname=%s, conditions=%s, kwargs=%s)"
            % (
                target,
                config,
                repositioning,
                dither,
                exp,
                nexp,
                midpoint,
                nsteps,
                stepsize,
                timeout,
                out_fname,
                conditions,
                kwargs,
            )
        )

    @classmethod
    @u.quantity_input(exp="s", timeout="s")
    def from_string(
        cls,
        string,
        target=None,
        config=None,
        repositioning=None,
        dither=0 * u.arcsec,
        exp=0 * u.s,
        nexp=1,
        midpoint=0,
        nsteps=7,
        stepsize=200,
        timeout=180 * u.s,
        out_fname=Path(""),
        conditions=[],
        **kwargs,
    ):
        """
        Create a `~pyscope.telrun.AutofocusField` or a `list` of `~pyscope.telrun.AutofocusField` objects from a `str` representation of a `~pyscope.telrun.AutofocusField`.
        The optional keyword arguments will overrride the parameters extracted from the `str` representation.

        Parameters
        ----------
        string : `str`, required

        config : `~pyscope.telrun.InstrumentConfiguration`, default : `None`

        repositioning : 2-tuple of `~astropy.units.Quantity`, default : `None`

        dither : `~astropy.units.Quantity`, default : 0 arcsec

        exp : `~astropy.units.Quantity`, default : 0 sec

        nexp : `int`, default : 1

        midpoint : `int`, default : 0

        nsteps : `int`, default : 7

        stepsize : `int`, default : 200

        timeout : `~astropy.units.Quantity`, default : 180 sec

        out_fname : `pathlib.Path`, default : Path("")

        conditions : `list` of `~pyscope.telrun.BoundaryCondition`, default : []

        **kwargs : `dict`, default : {}

        Returns
        -------
        `~pyscope.telrun.AutofocusField` or `list` of `~pyscope.telrun.AutofocusField`

        """
        logger.debug(
            "AutofocusField.from_string(string=%s, target=%s, config=%s, repositioning=%s, dither=%s, exp=%s, nexp=%i, midpoint=%i, nsteps=%i, stepsize=%i, timeout=%s, out_fname=%s, conditions=%s, kwargs=%s)"
            % (
                string,
                target,
                config,
                repositioning,
                dither,
                exp,
                nexp,
                midpoint,
                nsteps,
                stepsize,
                timeout,
                out_fname,
                conditions,
                kwargs,
            )
        )

    def __str__(self):
        """
        Return a `str` representation of the `~pyscope.telrun.AutofocusField`.

        Returns
        -------
        `str`
            A `str` representation of the `~pyscope.telrun.AutofocusField`.

        """
        logger.debug("AutofocusField().__str__() = %s" % self)

    @property
    def midpoint(self):
        """
        Return the midpoint of the autofocus sequence.

        Returns
        -------
        `int`
            The midpoint of the autofocus sequence.

        """
        logger.debug("AutofocusField().midpoint == %i" % self._midpoint)

    @midpoint.setter
    def midpoint(self, value):
        """
        Set the midpoint of the autofocus sequence.

        Parameters
        ----------
        value : `int`, required
            The midpoint of the autofocus sequence.

        """
        logger.debug("AutofocusField().midpoint = %i" % value)

    @property
    def nsteps(self):
        """
        Return the number of autofocus steps.

        Returns
        -------
        `int`
            The number of autofocus steps.

        """
        logger.debug("AutofocusField().nsteps == %i" % self._nsteps)

    @nsteps.setter
    def nsteps(self, value):
        """
        Set the number of autofocus steps.

        Parameters
        ----------
        value : `int`, required
            The number of autofocus steps.

        """
        logger.debug("AutofocusField().nsteps = %i" % value)

    @property
    def stepsize(self):
        """
        Return the step size of the autofocus sequence.

        Returns
        -------
        `int`
            The step size of the autofocus sequence.

        """
        logger.debug("AutofocusField().stepsize == %i" % self._stepsize)

    @stepsize.setter
    def stepsize(self, value):
        """
        Set the step size of the autofocus sequence.

        Parameters
        ----------
        value : `int`, required
            The step size of the autofocus sequence.

        """
        logger.debug("AutofocusField().stepsize = %i" % value)

    @property
    def timeout(self):
        """
        Return the autofocus sequence timeout.

        Returns
        -------
        `~astropy.units.Quantity`
            The autofocus sequence timeout.

        """
        logger.debug("AutofocusField().timeout == %s" % self._timeout)

    @timeout.setter
    def timeout(self, value):
        """
        Set the autofocus sequence timeout.

        Parameters
        ----------
        value : `~astropy.units.Quantity`, required
            The autofocus sequence timeout.

        """
        logger.debug("AutofocusField().timeout = %s" % value)
