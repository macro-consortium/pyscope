import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from .utils import *
from .observatory import Observatory

__version__ = '0.1.0'