from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Interval,
    String,
    Table,
    Uuid,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column, relationship

from ..db import Base
from .status import Status

logger = logging.getLogger(__name__)
logger.debug("_block.py")

observer_association_table = Table(
    "observer_association_table",
    Base.metadata,
    Column("block_uuid", ForeignKey("block.uuid")),
    Column("observer_uuid", ForeignKey("observer.uuid")),
)


class _Block(MappedAsDataclass, Base):
    """
    Represents a `~astropy.time.Time` range in a `~pyscope.scheduling.Schedule` attributed to an `~pyscope.scheduling.Observer`.

    A `~pyscope.scheduling._Block` can be used to represent allocated time with a `~pyscope.scheduling.ScheduleBlock`
    or unallocated time with an `~pyscope.scheduling.UnallocableBlock`. The `~pyscope.scheduling._Block` class is a base
    class that should not be instantiated directly. Instead, use the `~pyscope.scheduling.ScheduleBlock` or
    `~pyscope.scheduling.UnallocableBlock` subclasses.

    Parameters
    ----------
    name : `str`, default : ""
        A user-defined name for the `~pyscope.scheduling._Block`. This parameter does not change
        the behavior of the `~pyscope.scheduling._Block`, but it can be useful for identifying the
        `~pyscope.scheduling._Block` in a schedule.

    description : `str`, default : ""
        A user-defined description for the `~pyscope.scheduling._Block`. Similar to the `name`
        parameter, this parameter does not change the behavior of the `~pyscope.scheduling._Block`.

    observer : `~pyscope.scheduling.Observer`, required
        Associate this `~pyscope.scheduling._Block` with an `~pyscope.scheduling.Observer`. The `~pyscope.scheduling.Observer` is a
        bookkeeping object for an `~pyscope.observatory.Observatory` with multiple users/user groups.

    config : `~pyscope.telrun.InstrumentConfiguration`, required
        The `~pyscope.telrun.InstrumentConfiguration` to use for the `~pyscope.scheduling._Block`. This `~pyscope.telrun.InstrumentConfiguration` will be
        used to set the telescope's `~pyscope.telrun.InstrumentConfiguration` at the start of the `~pyscope.scheduling._Block` and
        will act as the default `~pyscope.telrun.InstrumentConfiguration` for all `~pyscope.scheduling.Field` objects in the
        `~pyscope.scheduling._Block` if a `~pyscope.telrun.InstrumentConfiguration` has not been provided. If a `~pyscope.scheduling.Field`
        has a different `~pyscope.telrun.InstrumentConfiguration`, it will override the block `~pyscope.telrun.InstrumentConfiguration` for the
        duration of the `~pyscope.scheduling.Field`.

    schedule : `~pyscope.scheduling.Schedule`, default : `None`
        The `~pyscope.scheduling.Schedule` that the `~pyscope.scheduling._Block` is associated with. This parameter is set automatically
        when the `~pyscope.scheduling._Block` is added to a `~pyscope.scheduling.Schedule` and is essentially a convenience parameter
        for quickly adding a `~pyscope.scheduling._Block` to a `~pyscope.scheduling.Schedule`.

    See Also
    --------
    pyscope.scheduling.ScheduleBlock : A subclass of `~pyscope.scheduling._Block` that is used to schedule `~pyscope.scheduling.Field` objects
        in a `~pyscope.scheduling.Schedule`.
    pyscope.scheduling.UnallocableBlock : A subclass of `~pyscope.scheduling._Block` that is used to represent unallocated time in a
        `~pyscope.scheduling.Schedule`.
    pyscope.telrun.InstrumentConfiguration : A class that represents the configuration of the telescope.
    pyscope.scheduling.Field : A class that represents a field to observe.
    """

    __tablename__ = "block"

    uuid: Mapped[Uuid] = mapped_column(
        Uuid, primary_key=True, nullable=False, init=False, default_factory=uuid4
    )
    version_id: Mapped[int] = mapped_column(Integer, nullable=False, init=False)
    block_type: Mapped[str] = mapped_column(String, nullable=False, init=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        init=False,
        default=datetime.now(tz=timezone.utc),
    )
    last_modified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        init=False,
        default=datetime.now(tz=timezone.utc),
        onupdate=datetime.now(tz=timezone.utc),
    )
    queued_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), init=False
    )
    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), init=False
    )

    status: Mapped[Status] = mapped_column(
        Enum, nullable=False, init=False, default=Status.UNSCHEDULED
    )

    name: Mapped[str | None] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String)

    observer: Mapped[List[Observer]] = relationship(
        secondary=observer_association_table
    )

    config_id: Mapped[Uuid] = mapped_column(
        ForeignKey("instrument_configuration.uuid"), init=False
    )
    config: Mapped[InstrumentConfiguration] = relationship(back_populates="blocks")

    start_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), init=False
    )
    duration: Mapped[timedelta | None] = mapped_column(
        Interval, default=timedelta(), init=False
    )

    schedule_id: Mapped[Uuid | None] = mapped_column(
        ForeignKey("schedule.uuid"), init=False
    )
    schedule: Mapped[Schedule | None] = relationship(back_populates="blocks")

    execution: Mapped[Execution | None] = relationship(back_populates="block")

    __mapper_args__ = {
        "version_id_col": version_id,
        "polymorphic_on": "block_type",
        "polymorphic_identity": "block",
    }

    def __post_init__(self):
        logger.debug("_Block = %s" % self)

    @hybrid_property
    def mid_time(self) -> datetime:
        return self.start_time + self.duration / 2

    @hybrid_property
    def end_time(self) -> datetime:
        return self.start_time + self.duration
