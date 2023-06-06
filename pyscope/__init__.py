'''A pure-Python library for controlling astronomical instrumentation.

The :doc:`pyscope </index>` package provides a set of tools to rapidly and easily control
astronomical instrumentation. It is designed to be modular and extensible,
allowing users to easily add support for new devices and observatories.




'''


import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
__version__ = '0.1.0'

from .utils import *
from .observatory import Observatory