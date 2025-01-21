import logging

from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger(__name__)

logger.debug("db imported")


class Base(DeclarativeBase):
    pass
