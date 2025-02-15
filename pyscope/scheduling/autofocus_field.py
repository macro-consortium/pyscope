from __future__ import annotations

import logging
from uuid import uuid4

from sqlalchemy import Float, ForeignKey, Integer, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .field import Field

logger = logging.getLogger(__name__)
logger.debug("autofocus_field.py")


class AutofocusField(Field):
    """
    A request to complete an autofocus sequence on a target field.

    The `~pyscope.scheduling.AutofocusField` is a special type of
    `~pyscope.scheduling.Field` that contains options to override the default
    autofocus parameters. The autofocus sequence will be run at the `midpoint`
    with the specified number of steps and step size. At each step, the
    the focus position will be changed by the `stepsize` and take `niter`
    exposures of `exp` duration.

    Parameters
    ----------
    target : `~pyscope.scheduling.Target`, required
        The target to observe. The target contains the data needed to determine
        the position of the target in the sky.

    exp : `float`, required
        The exposure time in seconds for each iteration of the field.

    config : `~pyscope.telrun.InstrumentConfiguration`, default : `None`
        The instrument configuration to use when observing the target. If
        `None`, the default configuration from the
        `~pyscope.scheduling.ObservingBlock` will be used.

    niter : `int`, default : 1
        The number of exposures to collect at each autofocus step.

        .. note::
            The behavior of `niter` is different for regular
            `~pyscope.scheduling.Field` objects. Ensure you have selected a
            value that is appropriate for the autofocus sequence.

    sleep_on_finish : `float`, default : 0
        The amount of time to sleep after the field is completed. This is useful
        for setting a short delay for specific cadence requirements.

    midpoint : `int`, default : 0
        The absolute step number at which to center the autofocus sequence.
        If 0, the autofocus sequence will occur at the current step number.

    nsteps : `int`, optional
        The number of autofocus steps to take. The total number of exposures
        will be `nexp * nsteps`.

    stepsize : `int`, optional
        The number of steps to move the focus position at each autofocus step.
    """

    midpoint: Mapped[int] = mapped_column(Integer, default=0)
    """
    The absolute step number at which to center the autofocus sequence.
    If 0, the autofocus sequence will occur at the current step number.
    """

    nsteps: Mapped[int | None] = mapped_column(
        Integer, nullable=True, kw_only=True
    )
    """
    The number of autofocus steps to take. The total number of exposures
    will be `niter * nsteps`.
    """

    stepsize: Mapped[int | None] = mapped_column(
        Integer, nullable=True, kw_only=True
    )
    """
    The number of steps to move the focus position at each autofocus step.
    """

    __mapper_args__ = {
        "polymorphic_identity": "autofocus_field",
    }

    def __post_init__(self) -> None:
        logger.debug("AutofocusField = %s" % self.__repr__)
