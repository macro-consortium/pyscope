import logging

from astropy import units as u

from .boundary_condition import BoundaryCondition

logger = logging.getLogger(__name__)


class CelestialBodyCondition:

    @staticmethod
    def _func(self, target, observer, time):
        pass

    @staticmethod
    def _lsq_func(self, value):
        pass

    @property
    def min_sep(self):
        pass

    @property
    def max_sep(self):
        pass

    @property
    def min_alt(self):
        pass

    @property
    def max_alt(self):
        pass

    @property
    def score_type(self):
        pass

    @property
    def inclusive(self):
        pass
