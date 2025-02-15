from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    declared_attr,
    has_inherited_table,
    mapped_column,
)

logger = logging.getLogger(__name__)
logger.debug("db.py")


class Base(DeclarativeBase, MappedAsDataclass):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    @declared_attr.directive
    def __mapper_args__(cls) -> dict:
        return {
            "version_id_col": cls.version_id,
            "polymorphic_on": cls.type,
        }

    @declared_attr.cascading
    @classmethod
    def uuid(cls) -> Mapped[Uuid]:
        """
        The universally unique identifier (UUID) for the database entry
        corresponding to the object. This UUID is generated automatically with
        `uuid.uuid4` when the object is created and is used to uniquely
        identify the object in the database. The UUID is a primary key for
        the table and is required to be unique for each entry. The UUID is
        not intended to be used as a human-readable identifier and should
        not be relied upon for that purpose.
        """
        if has_inherited_table(cls):
            return mapped_column(
                ForeignKey(cls.__mro__[-7].__name__.lower() + ".uuid"),
                primary_key=True,
                nullable=False,
                init=False,
            )
        else:
            return mapped_column(
                Uuid,
                primary_key=True,
                nullable=False,
                init=False,
                default_factory=uuid4,
            )

    version_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        init=False,
    )
    """
    The version ID for the database entry corresponding to the object. This
    ID is used to track changes to the object and is automatically updated by
    the database when the object is modified. The version ID is used to
    implement optimistic concurrency control to prevent multiple processes
    from updating the same object simultaneously. If a process attempts to
    modify an object and update the database entry with a stale version ID,
    a `sqlalchemy.orm.exc.StaleDataError` exception is raised. The process
    is then required to re-fetch the object from the database before
    attempting to update it again.

    For more information, see the
    `SQLAlchemy documentation <https://docs.sqlalchemy.org/en/20/orm/versioning.html>`__
    on versioning.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        init=False,
        default=datetime.now(tz=timezone.utc),
    )
    """
    The date and time when the object was created. This is automatically set
    to the current date and time in Universal Time (UTC) when the object is
    created.
    """

    last_modified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        init=False,
        default=datetime.now(tz=timezone.utc),
        onupdate=datetime.now(tz=timezone.utc),
    )
    """
    The date and time when the object was last modified. This is automatically
    set to the current date and time in Universal Time (UTC) when the object
    is modified.
    """

    type: Mapped[str | None] = mapped_column(String, init=False)
    """
    The polymorphic type of the object. This attribute is used to implement
    joined table inheritance in the database schema. The type is used to
    determine the correct table to query when loading the object from the
    database.

    In `pyscope`, this attribute is used widely throughout the package to
    map inheriting class structures to database tables. For example, the
    `Field` class is a base class for `DarkField`, `FlatField`, and
    `AutofocusField` classes, and the `type` attribute differentiates between
    these fields. Attributes shared across all field types are stored in the
    table corresponding to the `Field` class, and attributes specific to each
    field type are stored in the table corresponding to the specific field
    alongside a foreign key that links those attributes to the base class
    table.

    In most cases, this attribute can be ignored, as it is usually
    automatically set when the object is initialized. Observatories that
    are interested in implementing new custom classes that inherit from
    existing `pyscope` classes should set this parameter to a unique string
    that identifies the new class.

    For more information, see the
    `SQLAlchemy documentation <https://docs.sqlalchemy.org/en/20/orm/inheritance.html)>`__
    on inheritance.
    """


Base.__init__.__doc__ = ""
