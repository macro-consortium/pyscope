import logging

from astropy import units as u

from .boundary_condition import BoundaryCondition

logger = logging.getLogger(__name__)


class CelestialBodyCondition(BoundaryCondition):
    def __init__(
        self,
        body_name,
        min_sep=0 * u.deg,
        max_sep=180 * u.deg,
        min_alt=-90 * u.deg,
        max_alt=90 * u.deg,
        score_type="boolean",
        inclusive=True,
    ):
        """ """
        pass

    @classmethod
    def from_string(cls, string):
        pass

    def __str__(self):
        pass

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
