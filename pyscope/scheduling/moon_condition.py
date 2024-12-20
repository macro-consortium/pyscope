import logging

from .celestialbody_condition import CelestialBodyCondition

logger = logging.getLogger(__name__)


class MoonCondition(CelestialBodyCondition):
    def __init__(self, min_illum=0, max_illum=1, **kwargs):
        """ """
        pass

    @classmethod
    def from_string(cls, string, min_illum=None, max_illum=None, **kwargs):
        pass

    def __str__(self):
        pass
