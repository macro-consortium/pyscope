from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import List

from sqlalchemy import Column, DateTime, ForeignKey, Interval, Table, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base
from ._block import _Block

logger = logging.getLogger(__name__)
logger.debug("calibration_block.py")

field_cb_association_table = Table(
    "field_cb_association_table",
    Base.metadata,
    Column(
        "calibration_block_uuid",
        ForeignKey("calibration_block.uuid"),
        primary_key=True,
    ),
    Column("field_uuid", ForeignKey("field.uuid"), primary_key=True),
)


class CalibrationBlock(_Block):
    """
    Contains `~pyscope.scheduling.Field` objects that are used for collecting
    calibration data or performing calibration tasks.

    The `~pyscope.scheduling.CalibrationBlock` is distinguished from the
    `~pyscope.scheduling.ScheduleBlock` in that it is always scheduled first in
    the observing `~pyscope.scheduling.Schedule` and can contain several
    `~pyscope.scheduling.Field` types, including the
    `~pyscope.scheduling.DarkField`, `~pyscope.scheduling.FlatField`, and
    `~pyscope.scheduling.AutofocusField`.

    Parameters
    ----------
    name : `str`, default : ""
        A user-defined name for the `~pyscope.scheduling.CalibrationBlock`. This
        parameter does not change the behavior of the
        `~pyscope.scheduling.CalibrationBlock`, but it can be useful for
        identifying the `~pyscope.scheduling.CalibrationBlock` in a schedule.

    description : `str`, default : ""
        A user-defined description for the `~pyscope.scheduling.CalibrationBlock`.
        Similar to the `name` parameter, this parameter does not change the
        behavior of the `~pyscope.scheduling.CalibrationBlock`.

    observer : `~pyscope.scheduling.Observer`, required
        Associate this `~pyscope.scheduling.CalibrationBlock` with an
        `~pyscope.scheduling.Observer`. The `~pyscope.scheduling.Observer` is
        a bookkeeping object for an `~pyscope.observatory.Observatory` with
        multiple users/user groups.

    config : `~pyscope.telrun.InstrumentConfiguration`, required
        The `~pyscope.telrun.InstrumentConfiguration` to use for the
        `~pyscope.scheduling.CalibrationBlock`. This
        `~pyscope.telrun.InstrumentConfiguration` will be
        used to set the telescope's `~pyscope.telrun.InstrumentConfiguration`
        at the start of the `~pyscope.scheduling.CalibrationBlock` and will act as
        the default for all `~pyscope.scheduling.Field` objects in the
        `~pyscope.scheduling.CalibrationBlock` if one has not been provided. If a
        `~pyscope.scheduling.Field` has a different
        `~pyscope.telrun.InstrumentConfiguration`, it will override the block
        `~pyscope.telrun.InstrumentConfiguration` for the duration of the
        `~pyscope.scheduling.Field`.

    start_time : `~datetime.datetime`, required
        The start time of the `~pyscope.scheduling.CalibrationBlock`. Typically
        these blocks are constructed by the observatory manager, who must
        specify the start time of the block.

    duration : `~datetime.timedelta`, default=timedelta()
        The duration of the `~pyscope.scheduling.CalibrationBlock`. The
        duration may be manually set by the observatory manager. If the
        duration is not set, the `~pyscope.scheduling.Scheduler` will
        automatically compute the duration based on the
        `~pyscope.scheduling.TelrunModel` and the `~pyscope.scheduling.Field`
        objects in the `~pyscope.scheduling.CalibrationBlock`. The manual
        option is useful for blocking out time for calibration tasks that
        are not associated with any specific `~pyscope.scheduling.Field`.

    schedule : `~pyscope.scheduling.Schedule`, default : `None`
        The `~pyscope.scheduling.Schedule` that the
        `~pyscope.scheduling.CalibrationBlock` is associated with. This parameter
        is set automatically when the `~pyscope.scheduling.CalibrationBlock` is
        added to a `~pyscope.scheduling.Schedule` and is essentially a
        convenience parameter for quickly adding a
        `~pyscope.scheduling.CalibrationBlock` to a
        `~pyscope.scheduling.Schedule`.

    fields : `list` of `~pyscope.scheduling.Field`, default : []
        A list of `~pyscope.scheduling.Field` objects to be scheduled in
        the `~pyscope.scheduling.CalibrationBlock`. The
        `~pyscope.scheduling.Field` bjects will be executed in the order
        they are provided in the list. If the `~pyscope.scheduling.Field`
        objects have different `~pyscope.telrun.InstrumentConfiguration`
        objects, the `~pyscope.telrun.InstrumentConfiguration` object for the
        `~pyscope.scheduling.Field` will override the block
        `~pyscope.telrun.InstrumentConfiguration` for the duration
        of the `~pyscope.scheduling.Field`.

    """

    fields: Mapped[List[Field | None]] = relationship(
        secondary=field_cb_association_table, kw_only=True
    )
    """
    The list of `~pyscope.scheduling.Field` objects that are associated with
    the `~pyscope.scheduling.CalibrationBlock`. These
    `~pyscope.scheduling.Field` objects will be executed in the order they are
    listed in the `fields` attribute. Unlike other block types, the
    `~pyscope.scheduling.CalibrationBlock` does not have a `priority` attribute
    as they are always scheduled first. Additionally, the `fields` attribute
    accepts calibration fields like the `~pyscope.scheduling.DarkField`,
    `~pyscope.scheduling.FlatField`, and `~pyscope.scheduling.AutofocusField`.
    """

    __mapper_args__ = {
        "polymorphic_identity": "calibration_block",
    }

    def __post_init__(self) -> None:
        logger.debug("CalibrationBlock = %s" % self.__repr__)
