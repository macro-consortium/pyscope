from __future__ import annotations

import logging
from dataclasses import InitVar
from typing import Callable, Tuple

from sqlalchemy import Float, Uuid
from sqlalchemy.orm import Mapped, mapped_column

logger = logging.getLogger(__name__)
logger.debug("boundary_condition.py")

from ..db import Base


class BoundaryCondition(Base):
    """
    A class to hold a scoring function that evaluates a condition for a
    given target, time, and location.

    A generic class for defining a boundary condition as a function of
    `~astropy.time.Time`, `~astropy.coordinates.EarthLocation`, and
    `~astropy.coordinates.SkyCoord` used by the
    `~pyscope.telrun.Optimizer` inside the `~pyscope.telrun.Scheduler`
    to evaluate the quality of an observation across a range of times
    (and potentially locations) for a given target.

    Users will most likely not need to interact with this class directly,
    but instead will use the subclasses of
    `~pyscope.scheduling.BoundaryCondition` that are defined in the
    `~pyscope.scheduling` module. Commonly used subclasses include
    `~pyscope.scheduling.HourAngleCondition`,
    `~pyscope.scheduling.AirmassCondition`, and
    `~pyscope.scheduling.SunCondition`.

    The `~pyscope.telrun.SNRCondition` is also an excellent choice that
    takes advantage of properties of the
    `~pyscope.telrun.InstrumentConfiguration` and
    `~pyscope.scheduling.Field` to evaluate the
    `~pyscope.observatory.Observatory` class's signal-to-noise ratio model
    for scheduling over a range of times with dynamic conditions
    (e.g., a multi-night schedule across Moon bright time and dark time).
    This is a convenient way to simulate a complete observation over a
    range of conditions and times to evaluate the quality of the
    observation and gain access to the tools of the
    `~pyscope.telrun.Observatory` class's signal-to-noise ratio model, such
    as the image simulation tool for previewing the expected image and
    sources in the field.

    .. important::
        Developers and observatory managers should be aware that the `bc_func`
        and `lqs_func` attributes of this class are not mapped, so committing
        an instance of this class to the database will not store the functions
        in the database. This is by design, as storing functions in the
        database is *not recommended* due to the potential for security risks
        associated with the execution of arbitrary serialized code. Instead,
        the `~pyscope.scheduling.BoundaryCondition` class is designed to be
        used as a base class for defining custom boundary conditions that can
        be used in the scheduling optimization process. The `bc_func` and
        `lqs_func` functions should be defined in the subclass as static
        methods or regular methods.


    Parameters
    ----------
    bc_func : `Callable`, default : `None`
        The function to evaluate the condition. This function should take a
        `~astropy.coordinates.SkyCoord`, a `~astropy.time.Time`, and a
        `~astropy.coordinates.EarthLocation` as arguments and return a value
        that will be used by the `lqs_func` to evaluate the condition. If
        `None`, the `lqs_func` function will be used directly.

    lqs_func : `Callable`, default : `None`
        The function to convert the output of the `bc_func` into a linear
        quality score between `0` and `1`. This function should take the
        output of the `bc_func` and return a value between `0` and `1` that
        represents the quality of the condition. If `None`, the output of the
        `bc_func` will be used directly. In this case, the
        `~pyscope.scheduling.Scheduler` will typically try to normalize over
        all evaluated values from this boundary condition to a value between
        `0` and `1`, i.e., a `~pyscope.scheduling.LQSMinMax` with `min` and
        `max` values set to the minimum and maximum values of the `bc_func`
        output.

    weight : `float`, default : 1
        The weight of this condition relative to other conditions. This value
        is used by the `~pyscope.scheduling.Optimizer` inside the
        `~pyscope.scheduling.Scheduler` to compute the overall quality of a
        `~pyscope.scheduling.ScheduleBlock` based on the conditions that are
        evaluated. The weight should be a positive value, and the relative
        weight of each condition will be used to scale the output of the
        `lqs_func` function when computing the overall score. A weight of
        `0` will effectively disable the condition from being used in the
        optimization, and a weight of `1` is the default value. The weight
        can be set to any positive value to increase the relative importance
        of the condition. The composite linear quality score is typically
        computed as the geometric mean of the individual condition scores, so
        the weights are used to increase the power index of the geometric mean
        for each condition. Expressed mathematically:

        .. math::
            Q = \\left( \\prod_{i=1}^{N} q_i^{w_i} \\right)^{1 / \\sum_{i=1}^{N} w_i}

        where :math:`Q` is the composite quality score, :math:`q_i` is the
        quality score of the :math:`i`-th condition, and :math:`w_i` is the
        weight of the :math:`i`-th condition. The sum of the weights is used
        to normalize the composite quality score to a value between
        `0` and `1`. The default weight of `1` is used to give equal weight to
        all conditions, but users can adjust the weights to prioritize certain
        conditions over others. Since the weights are used as exponents in the
        geometric mean, `float` weights are possible.

    See Also
    --------
    pyscope.scheduling.CoordinateCondition
    pyscope.scheduling.HourAngleCondition
    pyscope.scheduling.AirmassCondition
    pyscope.scheduling.MoonCondition
    pyscope.scheduling.SunCondition
    pyscope.scheduling.TimeCondition
    pyscope.scheduling.SNRCondition
    """

    bc_func: InitVar[Callable] = None
    """
    The function to evaluate the condition. This function should take a
    `~astropy.coordinates.SkyCoord`, a `~astropy.time.Time`, and a
    `~astropy.coordinates.EarthLocation` as arguments and return a value
    that will be used by the `lqs_func` to evaluate the condition. If
    `None`, the `lqs_func` function will be used directly.

    .. important::
        This is not a mapped attribute and therefore will not be stored in
        the database. The `bc_func` is typically defined as a static method
        or regular method in a subclass of
        `~pyscope.scheduling.BoundaryCondition`.
    """

    lqs_func: InitVar[Callable] = None
    """
    The function to convert the output of the `bc_func` into a linear
    quality score between `0` and `1`. This function should take the
    output of the `bc_func` and return a value between `0` and `1` that
    represents the quality of the condition. If `None`, the output of the
    `bc_func` will be used directly. In this case, the
    `~pyscope.scheduling.Scheduler` will typically try to normalize over all
    evaluated values from this boundary condition to a value between `0` and
    `1`, i.e., a `~pyscope.scheduling.LQSMinMax` with `min` and `max` values
    set to the minimum and maximum values of the `bc_func` output.

    .. important::
        This is not a mapped attribute and therefore will not be stored in
        the database. The `lqs_func` is typically a subclass of the
        `~pyscope.scheduling.LQS` class with a `__call__` method that
        accepts the output of the `bc_func` as an argument and returns a
        value between `0` and `1`.
    """

    weight: Mapped[float | None] = mapped_column(Float, default=1)
    """
    The weight of this condition relative to other conditions. This value
    is used by the `~pyscope.scheduling.Optimizer` inside the
    `~pyscope.scheduling.Scheduler` to compute the overall quality of a
    `~pyscope.scheduling.ScheduleBlock` based on the conditions that are
    evaluated. The weight should be a positive value, and the relative
    weight of each condition will be used to scale the output of the
    `lqs_func` function when computing the overall score. A weight of
    `0` will effectively disable the condition from being used in the
    optimization, and a weight of `1` is the default value. The weight
    can be set to any positive value to increase the relative importance
    of the condition. The composite linear quality score is typically
    computed as the geometric mean of the individual condition scores, so
    the weights are used to increase the power index of the geometric mean
    for each condition. Expressed mathematically:

    .. math::
        Q = \\left( \\prod_{i=1}^{N} q_i^{w_i} \\right)^{1 / \\sum_{i=1}^{N} w_i}

    where :math:`Q` is the composite quality score, :math:`q_i` is the
    quality score of the :math:`i`-th condition, and :math:`w_i` is the
    weight of the :math:`i`-th condition. The sum of the weights is used
    to normalize the composite quality score to a value between
    `0` and `1`. The default weight of `1` is used to give equal weight to
    all conditions, but users can adjust the weights to prioritize certain
    conditions over others. Since the weights are used as exponents in the
    geometric mean, `float` weights are possible.
    """

    def __post_init__(
        self, bc_func: Callable | None, lqs_func: Callable | None
    ) -> None:
        self._bc_func = bc_func
        self._lqs_func = lqs_func
        logger.debug("BoundaryCondition = %s" % self.__repr__)

    def __call__(
        self, target: SkyCoord, time: Time, location: EarthLocation
    ) -> float:
        """
        Evaluate the `~pyscope.scheduling.BoundaryCondition` for a given
        target, time, and location.

        This is a shortcut for calling the `bc_func` and `lqs_func` functions
        directly. The `bc_func` function evaluates the condition for the
        target, time, and location and returns a value that is then passed to
        the `lqs_func` function to convert the value into a linear quality
        score between `0` and `1`. The `lqs_func` function is optional, and if
        not provided, the output of the `bc_func` function will be used
        directly as the quality score. The code is essentially equivalent to:

        .. code-block:: python

            if bc_func is not None and lqs_func is None:
                value = bc_func(target, time, location)
            elif lqs_func is not None:
                value = lqs_func(func(target, time, location))
            else:
                raise ValueError("Either bc_func or lqs_func must be provided.")

        Parameters
        ----------
        target : `~astropy.coordinates.SkyCoord`
            The target field to observe.

        time : `~astropy.time.Time`
            The time of the observation.

        location : `~astropy.coordinates.EarthLocation`
            The location of the observatory.

        Returns
        -------
        `float`
            A `float` value between `0` and `1` that represents the linear
            quality score of the condition.

        """
        logger.debug(
            "BoundaryCondition().__call__(target=%s, time=%s, location=%s)"
            % (target, time, location)
        )

        if self._bc_func is not None and self._lqs_func is None:
            value = self.calculate(target, time, location)
        elif self._lqs_func is not None:
            value = self.score(self.calculate(target, time, location))
        else:
            raise ValueError("Either func or lqs_func must be provided.")

        return value

    def calculate(
        self, target: SkyCoord, time: Time, location: EarthLocation
    ) -> Quantity | float:
        """
        Shorthand for calling the `bc_func` function directly.
        """
        return self._bc_func(target, time, location)

    def score(self, value: Quantity | float) -> float:
        """
        Shorthand for calling the `lqs_func` function directly.
        """
        return self._lqs_func(value)

    def plot(
        self, target: SkyCoord, time: Time, location: EarthLocation
    ) -> Tuple[Figure, Axes]:
        """
        To be implemented
        """
        raise NotImplementedError
