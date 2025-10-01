from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple
from uuid import uuid4

from sqlalchemy import (
    Column,
    ColumnElement,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Interval,
    String,
    Table,
    Uuid,
    type_coerce,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base
from .status import Status

logger = logging.getLogger(__name__)
logger.debug("schedule_block.py")

observer_block_association_table = Table(
    "observer_block_association_table",
    Base.metadata,
    Column("block_uuid", ForeignKey("block.uuid")),
    Column("observer_uuid", ForeignKey("observer.uuid")),
)

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


class ScheduleBlock(Base):
    """
    Represents a time range in a `~pyscope.scheduling.Schedule` attributed to
    an `~pyscope.scheduling.Observer`.

    A `~pyscope.scheduling.ScheduleBlock` can be used to represent allocated time
    with a `~pyscope.scheduling.ScheduleBlock` or unallocated time with an
    `~pyscope.scheduling.UnallocableBlock`. The `~pyscope.scheduling.ScheduleBlock`
    class is a base class that should not be instantiated directly. Instead,
    use the `~pyscope.scheduling.ScheduleBlock` or
    `~pyscope.scheduling.UnallocableBlock` subclasses.

    Parameters
    ----------
    name : `str`, default : ""
        A user-defined name for the `~pyscope.scheduling._Block`. This
        parameter does not change the behavior of the
        `~pyscope.scheduling._Block`, but it can be useful for identifying
        the `~pyscope.scheduling._Block` in a schedule.

    description : `str`, default : ""
        A user-defined description for the `~pyscope.scheduling._Block`.
        Similar to the `name` parameter, this parameter does not change the
        behavior of the `~pyscope.scheduling._Block`.

    observer : `~pyscope.scheduling.Observer`, required
        Associate this `~pyscope.scheduling._Block` with an
        `~pyscope.scheduling.Observer`. The `~pyscope.scheduling.Observer` is
        a bookkeeping object for an `~pyscope.observatory.Observatory` with
        multiple users/user groups.

    config : `~pyscope.telrun.InstrumentConfiguration`, required
        The `~pyscope.telrun.InstrumentConfiguration` to use for the
        `~pyscope.scheduling._Block`. This
        `~pyscope.telrun.InstrumentConfiguration` will be
        used to set the telescope's `~pyscope.telrun.InstrumentConfiguration`
        at the start of the `~pyscope.scheduling._Block` and will act as the
        default for all `~pyscope.scheduling.Field` objects in the
        `~pyscope.scheduling._Block` if one has not been provided. If a
        `~pyscope.scheduling.Field` has a different
        `~pyscope.telrun.InstrumentConfiguration`, it will override the block
        `~pyscope.telrun.InstrumentConfiguration` for the duration of the
        `~pyscope.scheduling.Field`.

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

    See Also
    --------
    pyscope.scheduling.ScheduleBlock : A subclass of
        `~pyscope.scheduling._Block` that is used to schedule
        `~pyscope.scheduling.Field` objects in a
        `~pyscope.scheduling.Schedule`.
    pyscope.scheduling.UnallocableBlock : A subclass of
        `~pyscope.scheduling._Block` that is used to represent unallocated
        time in a `~pyscope.scheduling.Schedule`.
    pyscope.telrun.InstrumentConfiguration : A class that represents the
        configuration of the telescope.
    pyscope.scheduling.Field : A class that represents a field to observe.
    """

    queued_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), init=False
    )
    """
    The time that the block was requested to be scheduled. This parameter
    is set automatically when the block is added to a
    `~pyscope.scheduling.Schedule` and is commonly used to track the order in
    which block objects were added for some prioritization schemes.
    """

    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), init=False
    )
    """
    The time that the block was scheduled. This parameter is set automatically
    when the block is scheduled by the `~pyscope.scheduling.Scheduler`.
    """

    status: Mapped[Status] = mapped_column(
        Enum, nullable=False, init=False, default=Status.UNSCHEDULED
    )
    """
    The status of the block. This parameter is used to track the state of
    the block and is set automatically at various stages of the scheduling
    and execution process. The `status` parameter is an `~enum.Enum` with the
    following possible values:

    * `~pyscope.scheduling.Status.UNSCHEDULED` : The block has not been
      scheduled.

    * `~pyscope.scheduling.Status.EXPIRED` : The block has expired and cannot
      be scheduled.

    * `~pyscope.scheduling.Status.INVALID` : The block is invalid and cannot
      be scheduled.

    * `~pyscope.scheduling.Status.QUEUED` : The block is queued for
      scheduling.

    * `~pyscope.scheduling.Status.SCHEDULED` : The block has been assigned a
      start time and is therefore scheduled.

    * `~pyscope.scheduling.Status.FAILED` : The block failed to execute.

    * `~pyscope.scheduling.Status.CANCELLED` : The block was cancelled before
      execution began.

    * `~pyscope.scheduling.Status.IN_PROGRESS` : The block is currently
      executing.

    * `~pyscope.scheduling.Status.COMPLETED` : The block has completed
      execution.

    """

    name: Mapped[str | None] = mapped_column(String)
    """
    A user-defined name for the block. This parameter does not change
    the behavior of the block, but it can be useful for identifying the
    block in a schedule.
    """

    description: Mapped[str | None] = mapped_column(String)
    """
    A user-defined description for the block. Similar to the `name`
    parameter, this parameter does not change the behavior of the block.
    """

    block_type: Mapped[str | None] = mapped_column(String)
    """
    The type of the block. Can be set to either "dynamic" (default) or "static".
    """

    earliest_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), init=False
    )
    """
    The earliest schedulable start time for a dynamic block. 
    """

    latest_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), init=False
    )
    """
    The latest schedulable start time for a dynamic block.
    """

    observer: Mapped[List[Observer]] = relationship(
        secondary=observer_block_association_table
    )
    """
    The list of `~pyscope.scheduling.Observer` objects associated with the
    block. A block can be associated with just an
    `~pyscope.scheduling.Observer` or multiple `~pyscope.scheduling.Observer`
    objects. These `~pyscope.scheduling.Observer` objects are used to track
    the users or user groups that are responsible for the block.

    .. attention::
        All block objects must be associated with at least one
        `~pyscope.scheduling.Observer`.
    """

    config_uuid: Mapped[Uuid] = mapped_column(
        ForeignKey("instrument_configuration.uuid"), init=False
    )
    """
    The UUID for the `~pyscope.telrun.InstrumentConfiguration` used as the
    default configuration for the block. See the `config` parameter for more
    information.
    """

    config: Mapped[InstrumentConfiguration] = relationship(
        back_populates="blocks"
    )
    """
    The `~pyscope.telrun.InstrumentConfiguration` used as the default
    configuration for the block. A default
    `~pyscope.telrun.InstrumentConfiguration` must be provided when creating
    a new block.

    .. attention::
        A default `~pyscope.telrun.InstrumentConfiguration` must be provided
        when creating a new block.
    """

    start_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), init=False
    )
    """
    The start time of the block. This parameter is typically set by the
    `~pyscope.scheduling.Scheduler` when the block is scheduled but can be
    manually set by the user for certain block types.
    """

    duration: Mapped[timedelta | None] = mapped_column(
        Interval, default=timedelta(), init=False
    )
    """
    The duration of the block. Typically computed by the
    `~pyscope.scheduling.Scheduler` using the
    `~pyscope.scheduling.TelrunModel`, it can also be manually set by the
    user for certain block types.
    """

    execution_block: Mapped[ExecutionBlock | None] = relationship(
        back_populates="block", init=False
    )
    """
    The `~pyscope.telrun.ExecutionBlock` associated with the block.
    The `~pyscope.telrun.ExecutionBlock` is generated by
    `~pyscope.telrun.TelrunOperator` and contains information, statuses, and
    logs related to the execution of the block for review by the requesting
    user and debugging purposes by the observatory staff.
    """

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

    def __post_init__(self) -> None:
        logger.debug("_Block = %s" % self.__repr__)

    @hybrid_property
    def mid_time(self) -> datetime:
        """
        The midpoint time of the block. Automatically computed as the start
        time plus half the duration of the block.
        """
        return self.start_time + self.duration / 2

    @mid_time.inplace.setter
    def _mid_time_setter(self, value: datetime) -> None:
        self.start_time = value - self.duration / 2
        self.end_time = value + self.duration / 2

    @mid_time.inplace.expression
    @classmethod
    def _mid_time_expression(cls) -> ColumnElement[DateTime]:
        return type_coerce(cls.start_time + cls.duration / 2, DateTime)

    @mid_time.inplace.update_expression
    @classmethod
    def _mid_time_update_expression(
        cls, value: DateTime
    ) -> List[Tuple[DateTime, DateTime]]:
        return [
            (cls.start_time, type_coerce(value - cls.duration / 2, DateTime)),
            (cls.end_time, type_coerce(value + cls.duration / 2, DateTime)),
        ]

    @hybrid_property
    def end_time(self) -> datetime:
        """
        The end time of the block. Automatically computed as the start time
        plus the duration of the block.
        """
        return self.start_time + self.duration

    @end_time.inplace.setter
    def _end_time_setter(self, value: datetime) -> None:
        self.start_time = value - self.duration

    @end_time.inplace.expression
    @classmethod
    def _end_time_expression(cls) -> ColumnElement[DateTime]:
        return type_coerce(cls.start_time + cls.duration, DateTime)

    @end_time.inplace.update_expression
    @classmethod
    def _end_time_update_expression(
        cls, value: DateTime
    ) -> List[Tuple[DateTime, DateTime]]:
        return [(cls.start_time, type_coerce(value - cls.duration, DateTime))]

