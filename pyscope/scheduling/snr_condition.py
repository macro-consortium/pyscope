import logging

from .boundary_condition import BoundaryCondition

logger = logging.getLogger(__name__)


class SNRCondition:
    def __init__(
        self, min_snr=None, max_snr=None, score_type="boolean", inclusive=True
    ):
        """ """
        pass

    @classmethod
    def from_string(
        cls,
        string,
        min_snr=None,
        max_snr=None,
        score_type=None,
        inclusive=None,
    ):
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
    def min_snr(self):
        pass

    @property
    def max_snr(self):
        pass

    @property
    def score_type(self):
        pass

    @property
    def inclusive(self):
        pass
