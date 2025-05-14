import logging

from astropy import units as u

from .boundary_condition import BoundaryCondition

logger = logging.getLogger(__name__)


class SunCondition:
    def __init__(self, **kwargs):
        """ """
        pass

    @classmethod
    def from_string(cls, string, **kwargs):
        pass

    def __str__(self):
        pass
