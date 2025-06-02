from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import DateTime, ForeignKey, Interval, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from ._block import _Block

logger = logging.getLogger(__name__)
logger.debug("unallocable_block.py")


class UnallocableBlock(_Block):
    """
    A time range that is not allocable for scheduling.

    The `~pyscope.scheduling.UnallocableBlock` is used to block out time in the
    `~pyscope.scheduling.Schedule` that is not available for scheduling. This
    could be used for maintenance tasks, calibration tasks, or other
    observatory tasks that are not associated with a specific
    `~pyscope.scheduling.Field`. Commonly, this block type is used to remove
    the day time from the schedule for ease of computing statistics and
    logs detailing schedule efficiency.

    Parameters
    ----------
    name : `str`, default : ""
        A user-defined name for the `~pyscope.scheduling.UnallocableBlock`. This
        parameter does not change the behavior of the
        `~pyscope.scheduling.UnallocableBlock`, but it can be useful for
        identifying the `~pyscope.scheduling.UnallocableBlock` in a schedule.

    description : `str`, default : ""
        A user-defined description for the
        `~pyscope.scheduling.UnallocableBlock`. Similar to the `name` parameter,
        this parameter does not change the behavior of the
        `~pyscope.scheduling.UnallocableBlock`.

    observer : `~pyscope.scheduling.Observer`, required
        Associate this `~pyscope.scheduling.UnallocableBlock` with an
        `~pyscope.scheduling.Observer`. The `~pyscope.scheduling.Observer` is
        a bookkeeping object for an `~pyscope.observatory.Observatory` with
        multiple users/user groups. Typically, this is set to the observatory
        manager or the observatory itself.

    config : `~pyscope.telrun.InstrumentConfiguration`, required
        The `~pyscope.telrun.InstrumentConfiguration` to use for the
        `~pyscope.scheduling.UnallocableBlock`. This
        `~pyscope.telrun.InstrumentConfiguration` will be
        used to set the telescope's `~pyscope.telrun.InstrumentConfiguration`
        at the start of the `~pyscope.scheduling.UnallocableBlock`. Typically,
        this is set to the default instrument configuration for the observatory
        or a "park" position.

    start_time : `~datetime.datetime`, required
        The start time of the `~pyscope.scheduling.UnallocableBlock`. Typically
        these blocks are constructed by the observatory manager, who must
        specify the start time of the block.

    duration : `~datetime.timedelta`, default=timedelta()
        The duration of the `~pyscope.scheduling.UnallocableBlock`. The
        duration may be manually set by the observatory manager.

    schedule : `~pyscope.scheduling.Schedule`, default : `None`
        The `~pyscope.scheduling.Schedule` that the
        `~pyscope.scheduling.UnallocableBlock` is associated with.
        This parameter is set automatically when the
        `~pyscope.scheduling.UnallocableBlock` is added to a
        `~pyscope.scheduling.Schedule` and is essentially a
        convenience parameter for quickly adding a
        `~pyscope.scheduling.UnallocableBlock` to a
        `~pyscope.scheduling.Schedule`.

    """

    __mapper_args__ = {
        "polymorphic_identity": "unallocable_block",
    }

    def __post_init__(self) -> None:
        logger.debug("UnallocableBlock = %s" % self.__repr__)
