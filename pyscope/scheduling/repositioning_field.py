from __future__ import annotations

import logging
from typing import Tuple
from uuid import uuid4

from sqlalchemy import Float, ForeignKey, Integer, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .field import Field

logger = logging.getLogger(__name__)
logger.debug("repositioning_field.py")


class RepositioningField(Field):
    """
    A request to iteratively update the pointing of the telescope.

    The `~pyscope.scheduling.RepositioningField` is a special type of
    `~pyscope.scheduling.Field` that is used to iteratively reposition the
    pointing by placing the target at a specific location on the detector. This
    is implemented by using a WCS solver on sequential images and adjusting
    the pointing to place the target at the desired location.

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
        The maximum number of nudging iterations.

        .. note::
            The behavior of `niter` is different for regular
            `~pyscope.scheduling.Field` objects. Ensure you have selected a
            value that is appropriate for the repositioning sequence.

    sleep_on_finish : `float`, default : 0
        The amount of time to sleep after the field is completed. This is useful
        for setting a short delay for specific cadence requirements.

    detector_coords : `tuple`, default : (0, 0)
        The desired location on the detector to place the target. This is
        specified as a tuple of `(x, y)` coordinates.

    initial_offset : `tuple`, default : (0, 0)
        The initial offset from the target position in detector coordinates.
        This is specified as a tuple of `(dx, dy)` coordinates.

    check_and_refine : `bool`, default : True
        If `True`, an image will be taken after the iteration and checked
        against specified tolerances.

    do_initial_slew : `bool`, default : True
        If `True`, the telescope will attempt to slew to the target before
        taking the initial image. Turning this off is useful for when the
        telescope is already on target and the initial image is used to
        ensure the target has not drifted and will make corrections as needed.

    tolerance : `float`, default : 5
        The tolerance in pixels to accept the final position of the target.

    """

    detector_coords: Mapped[Tuple[float, float]] = mapped_column(
        Integer, nullable=False, kw_only=True
    )

    initial_offset: Mapped[Tuple[float, float]] = mapped_column(
        Integer, nullable=False, kw_only=True
    )

    check_and_refine: Mapped[bool] = mapped_column(
        Integer, nullable=False, default=True, kw_only=True
    )

    do_initial_slew: Mapped[bool] = mapped_column(
        Integer, nullable=False, default=True, kw_only=True
    )

    tolerance: Mapped[float] = mapped_column(
        Float, nullable=False, default=5, kw_only=True
    )

    __mapper_args__ = {
        "polymorphic_identity": "repositioning_field",
    }

    def __post_init__(self) -> None:
        logger.debug("RepositioningField = %s" % self.__repr__)
