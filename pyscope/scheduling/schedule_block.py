from __future__ import annotations

import logging
from typing import List

from sqlalchemy import Column, ForeignKey, Integer, Table, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base
from ._block import _Block

logger = logging.getLogger(__name__)
logger.debug("scheduleScheduleBlock.py")

condition_sb_association_table = Table(
    "condition_sb_association_table",
    Base.metadata,
    Column(
        "schedule_block_uuid",
        ForeignKey("schedule_block.uuid"),
        primary_key=True,
    ),
    Column(
        "boundary_condition_uuid",
        ForeignKey("boundary_condition.uuid"),
        primary_key=True,
    ),
)

field_sb_association_table = Table(
    "field_sb_association_table",
    Base.metadata,
    Column("schedule_block_uuid", ForeignKey("schedule_block.uuid")),
    Column("field_uuid", ForeignKey("field.uuid")),
)


class ScheduleBlock(_Block):
    """
    A class to contain a list of `~pyscope.scheduling.Field` objects to be
    scheduled as a single time range in the observing
    `~pyscope.scheduling.Schedule`.

    The `~pyscope.scheduling.ScheduleBlock` is the fundamental unit that users
    interact with when creating observing requests. It is a container for one
    or more `~pyscope.scheduling.Field` objects, which represent the actual
    observing targets. The `~pyscope.scheduling.ScheduleBlock` also contains
    metadata about the block used by the `~pyscope.scheduling.Scheduler` to
    determine the best possible schedule using the
    `~pyscope.scheduling.BoundaryCondition` objects and the priority level
    provided when instantiating the `~pyscope.scheduling.ScheduleBlock`.

    The `~pyscope.scheduling.Scheduler` can also take advantage of the
    `~pyscope.scheduling.Field` objects themselves to make scheduling
    decisions. This mode is optimal for a `~pyscope.scheduling.ScheduleBlock`
    that contains only one `~pyscope.scheduling.Field` or multiple
    `~pyscope.scheduling.Field` objects that have small angular separations on
    the sky. For larger separations, it is recommended to create separate
    `~pyscope.scheduling.ScheduleBlock` objects for each
    `~pyscope.scheduling.Field`.

    Parameters
    ----------
    name : `str`, default : ""
        A user-defined name for the `~pyscope.scheduling.ScheduleBlock`. This
        parameter does not change the behavior of the
        `~pyscope.scheduling.ScheduleBlock`, but it can be useful for
        identifying the `~pyscope.scheduling.ScheduleBlock` in a schedule.

    description : `str`, default : ""
        A user-defined description for the `~pyscope.scheduling.ScheduleBlock`.
        Similar to the `name` parameter, this parameter does not change the
        behavior of the `~pyscope.scheduling.ScheduleBlock`.

    observer : `~pyscope.scheduling.Observer`, required
        Associate this `~pyscope.scheduling.ScheduleBlock` with an
        `~pyscope.scheduling.Observer`. The `~pyscope.scheduling.Observer` is
        a bookkeeping object for an `~pyscope.observatory.Observatory` with
        multiple users/user groups.

    config : `~pyscope.telrun.InstrumentConfiguration`, required
        The `~pyscope.telrun.InstrumentConfiguration` to use for the
        `~pyscope.scheduling.ScheduleBlock`. This
        `~pyscope.telrun.InstrumentConfiguration` will be
        used to set the telescope's `~pyscope.telrun.InstrumentConfiguration`
        at the start of the `~pyscope.scheduling.ScheduleBlock` and will act as
        the default for all `~pyscope.scheduling.Field` objects in the
        `~pyscope.scheduling.ScheduleBlock` if one has not been provided. If a
        `~pyscope.scheduling.Field` has a different
        `~pyscope.telrun.InstrumentConfiguration`, it will override the block
        `~pyscope.telrun.InstrumentConfiguration` for the duration of the
        `~pyscope.scheduling.Field`.

    schedule : `~pyscope.scheduling.Schedule`, default : `None`
        The `~pyscope.scheduling.Schedule` that the
        `~pyscope.scheduling.ScheduleBlock` is associated with. This parameter
        is set automatically when the `~pyscope.scheduling.ScheduleBlock` is
        added to a `~pyscope.scheduling.Schedule` and is essentially a
        convenience parameter for quickly adding a
        `~pyscope.scheduling.ScheduleBlock` to a
        `~pyscope.scheduling.Schedule`.

    priority : `int`, default : 0
        The priority level of the `~pyscope.scheduling.ScheduleBlock`. The
        `~pyscope.scheduling.Prioritizer` inside the
        `~pyscope.scheduling.Scheduler` will use this parameter to determine
        the best possible schedule. The highest priority level is 1 and
        decreasing priority levels are integers above 1. The lowest priority is
        0, which is the default value. Tiebreakers are usually determined by
        the `~pyscope.scheduling.Prioritizer` inside the
        `~pyscope.scheduling.Scheduler`, but some more advanced scheduling
        algorithms may use results from the
        `~pyscope.scheduling.Optimizer` to break ties.

    project : `~pyscope.scheduling.Project`, default : `None`
        The `~pyscope.scheduling.Project` object to assign this
        `~pyscope.scheduling.ScheduleBlock` to. This parameter does not change
        the behavior of the `~pyscope.scheduling.ScheduleBlock`, but it can be
        useful for tracking which project the
        `~pyscope.scheduling.ScheduleBlock` is associated with and for
        generating reports for the project. Each
        `~pyscope.scheduling.ScheduleBlock` can only be assigned to one
        `~pyscope.scheduling.Project`.

    conditions : `list` of `~pyscope.scheduling.BoundaryCondition`, default : []
        A list of `~pyscope.scheduling.BoundaryCondition` objects that define
        the constraints for all `~pyscope.scheduling.Field` objects in the
        `~pyscope.scheduling.ScheduleBlock`. The `~pyscope.telrun.Optimizer`
        inside the `~pyscope.scheduling.Scheduler` will use the
        `~pyscope.scheduling.BoundaryCondition` objects to determine the best
        possible schedule.

    fields : `list` of `~pyscope.scheduling.Field`, default : []
        A list of `~pyscope.scheduling.Field` objects to be scheduled in
        the `~pyscope.scheduling.ScheduleBlock`. The
        `~pyscope.scheduling.Field` bjects will be executed in the order
        they are provided in the list. If the `~pyscope.scheduling.Field`
        objects have different `~pyscope.telrun.InstrumentConfiguration`
        objects, the `~pyscope.telrun.InstrumentConfiguration` object for the
        `~pyscope.scheduling.Field` will override the block
        `~pyscope.telrun.InstrumentConfiguration` for the duration
        of the `~pyscope.scheduling.Field`.

        .. note::
            A `~pyscope.scheduling.ScheduleBlock' can only contain
            `~pyscope.scheduling.Field` objects. If you want to schedule
            a `~pyscope.scheduling.DarkField`, `~pyscope.scheduling.FlatField`,
            or an `~pyscope.scheduling.AutoFocusField`, you must use a
            `~pyscope.scheduling.CalibrationBlock`.

    """

    '''__tablename__ = "schedule_block"'''

    """uuid: Mapped[Uuid] = mapped_column(
        ForeignKey("block.uuid"),
        primary_key=True,
        init=False,
    )"""

    priority: Mapped[int] = mapped_column(Integer, default=0)
    """
    The priority level of the `~pyscope.scheduling.ScheduleBlock`. The
    `~pyscope.scheduling.Prioritizer` inside the `~pyscope.scheduling.Scheduler`
    will use this parameter to determine the best possible schedule. The highest
    priority level is 1 and decreasing priority levels are integers above 1. The
    lowest priority is 0, which is the default value. Tiebreakers are usually
    determined by the `~pyscope.scheduling.Prioritizer` inside the
    `~pyscope.scheduling.Scheduler`, but some more advanced scheduling
    algorithms may use results from the `~pyscope.scheduling.Optimizer` to break
    ties.
    """

    project_uuid: Mapped[Uuid | None] = mapped_column(
        ForeignKey("project.uuid"), init=False
    )
    """
    The `~pyscope.scheduling.Project` UUID. See the `project` parameter for more
    information.
    """

    project: Mapped[Project | None] = relationship(
        back_populates="schedule_blocks", kw_only=True
    )
    """
    The `~pyscope.scheduling.Project` object to assign this
    `~pyscope.scheduling.ScheduleBlock` to. This parameter does not change the
    behavior of the `~pyscope.scheduling.ScheduleBlock`, but it can be useful
    for bookkeeping.
    """

    conditions: Mapped[List[BoundaryCondition | None]] = relationship(
        secondary=condition_sb_association_table, kw_only=True
    )
    """
    A list of `~pyscope.scheduling.BoundaryCondition` objects that define the
    constraints for all `~pyscope.scheduling.Field` objects in the
    `~pyscope.scheduling.ScheduleBlock`. The `~pyscope.telrun.Optimizer` inside
    the `~pyscope.scheduling.Scheduler` will use the
    `~pyscope.scheduling.BoundaryCondition` objects to determine the best
    possible time to observe this `~pyscope.scheduling.ScheduleBlock`.
    """

    fields: Mapped[List[Field | None]] = relationship(
        secondary=field_sb_association_table, kw_only=True
    )
    """
    A list of `~pyscope.scheduling.Field` objects to be scheduled in the
    `~pyscope.scheduling.ScheduleBlock`. The `~pyscope.scheduling.Field`
    objects will be executed in the order they are provided in the list.
    """

    __mapper_args__ = {
        "polymorphic_identity": "schedule_block",
    }

    def __post_init__(self) -> None:
        logger.debug("ScheduleBlock = %s" % self.__repr__)
