from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import List
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base

logger = logging.getLogger(__name__)
logger.debug("field.py")


class Field(Base):
    """
    Contains an individual `~pyscope.scheduling.Target` and the associated
    `~pyscope.telrun.InstrumentConfiguration` to observe the target.

    The `~pyscope.scheduling.Field` is the fundamental unit of observation in
    the `~pyscope.scheduling.ScheduleBlock`. It contains the target to observe
    and the configuration to use when observing the target. The field also
    contains the number of iterations to perform on the target. This is useful
    for repeating the observation of a target multiple times.

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

    collate : `bool`, default : `True`
        If `config` has multiple configurations, then this field determines how
        `niter` iterations are handled. If `collate` is set to `False`,
        then `niter` iterations of the first configuration, the second, and so on
        will be executed sequentially (e.g., 1, 1, 1,  2, 2, 2,  3, 3, 3,  4, 4, 4).
        If `collate` is set to `True` (default), then the first configuration will be
        followed by the second, and so on until all configurations have been
        executed once in order, then that process will repeat `niter` times
        (e.g., 1, 2, 3, 4,  1, 2, 3, 4,  1, 2, 3, 4).

    niter : `int`, default : 1
        The number of iterations of this field to perform. This parameter is
        used to repeat the observation of the field multiple times. For
        example, if an observer wanted to use multiple exposures to observe a
        field, they could set this parameter to take those data in a single
        field instead of creating multiple fields for the same target.

    sleep_on_finish : `float`, default : 0
        The amount of time to sleep after the field is completed. This is useful
        for setting a short delay for specific cadence requirements.

    See Also
    --------
    pyscope.scheduling.RepositioningField : A special type of
        `~pyscope.scheduling.Field` that is used to iteratively reposition the
        pointing by placing the target at a specific location on the detector.
    pyscope.scheduling.AutofocusField : A special type of
        `~pyscope.scheduling.Field` that is used to focus the telescope.
    pyscope.scheduling.DarkField : A special type of
        `~pyscope.scheduling.Field` that is used to capture dark frames.
    pyscope.scheduling.FlatField : A special type of
        `~pyscope.scheduling.Field` that is used to capture flat fields.
    """

    target_uuid: Mapped[Uuid] = mapped_column(
        ForeignKey("target.uuid"),
        nullable=False,
        init=False,
    )
    """
    The UUID of the `~pyscope.scheduling.Target` to observe.
    See the `target` attribute for more information.
    """

    target: Mapped[Target] = relationship(back_populates="fields")
    """
    The `~pyscope.scheduling.Target` to observe. The target contains the data
    needed to determine the position of the target in the sky.
    """

    exp: Mapped[float] = mapped_column(Float, nullable=False)
    """
    The exposure time in seconds for each iteration of the field.
    """

    config_uuid: Mapped[Uuid] = mapped_column(
        ForeignKey("instrument_configuration.uuid"),
        nullable=True,
        init=False,
    )
    """
    The UUID for the `~pyscope.telrun.InstrumentConfiguration`.
    See the `config` parameter for more information.
    """

    config: Mapped[InstrumentConfiguration | None] = relationship(
        back_populates="fields"
    )
    """
    The `~pyscope.telrun.InstrumentConfiguration` to use when observing the
    target.

    .. note::
        This parameter is optional and will default to the
        value of the `~pyscope.scheduling.ObservingBlock` default
        `~pyscope.telrun.InstrumentConfiguration` if not specified. It is
        often useful to set the configuration on the ObservingBlock level
        and separate the configuration from the field.

    """

    collate: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )
    """
    If `config` has multiple configurations, then this field determines how
    `niter` iterations are handled. If `collate` is set to `False`,
    then `niter` iterations of the first configuration, the second, and so on
    will be executed sequentially (e.g., 1, 1, 1,  2, 2, 2,  3, 3, 3,  4, 4, 4).
    If `collate` is set to `True` (default), then the first configuration will be
    followed by the second, and so on until all configurations have been
    executed once in order, then that process will repeat `niter` times
    (e.g., 1, 2, 3, 4,  1, 2, 3, 4,  1, 2, 3, 4). This option is useful for
    situations like, e.g., iterating over filters in a time series.
    """

    niter: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    """
    The number of iterations of this field to perform. This parameter is used
    to repeat the observation of the field multiple times. For example, if an
    observer wanted to use multiple exposures to observe a field, they could
    set this parameter to take those data in a single field instead of creating
    multiple fields for the same target.
    """

    sleep_on_finish: Mapped[float] = mapped_column(
        Float, nullable=False, default=0
    )
    """
    The amount of time to sleep after the field is completed. This is useful
    for setting a short delay for specific cadence requirements.
    """

    def __post_init__(self) -> None:
        logger.debug("_Field = %s" % self.__repr__)
