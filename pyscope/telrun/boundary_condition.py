import logging

logger = logging.getLogger(__name__)


class BoundaryCondition:
    def __init__(
        self,
        func=None,
        lqs_func=None,
        weight=1,
        **kwargs,
    ):
        """
        A class to hold a scoring function that evaluates a condition for a given target, time, and location.

        A generic class for defining a boundary condition as a function of `~astropy.time.Time`,
        `~astropy.coordinates.EarthLocation`, and `~astropy.coordinates.SkyCoord` used by the
        `~pyscope.telrun.Optimizer` inside the `~pyscope.telrun.Scheduler` to evaluate the quality
        of an observation across a range of times (and potentially locations) for a given target.

        Users will most likely not need to interact with this class directly, but instead will use
        the subclasses of `~pyscope.telrun.BoundaryCondition` that are defined in the `~pyscope.telrun`
        module. Commonly used subclasses include `~pyscope.telrun.HourAngleCondition`,
        `~pyscope.telrun.AirmassCondition`, and `~pyscope.telrun.SunCondition`.

        The `~pyscope.telrun.SNRCondition` is also an excellent choice that takes advantage of properties
        of the `~pyscope.telrun.InstrumentConfiguration` and `~pyscope.telrun.LightField` to evaluate the
        `~pyscope.observatory.Observatory` class's signal-to-noise ratio model for scheduling over a range
        of times with dynamic conditions (e.g., a multi-night schedule across Moon bright time and dark time).
        This is a convenient way to simulate a complete observation over a range of conditions and times
        to evaluate the quality of the observation and gain access to the tools of the
        `~pyscope.telrun.Observatory` class's signal-to-noise ratio model, such as the image simulation tool
        for previewing the expected image and sources in the field.

        Parameters
        ----------
        func : `function`, default : `None`
            The function to evaluate the condition. This function should take a `~astropy.coordinates.SkyCoord`,
            a `~astropy.time.Time`, and a `~astropy.coordinates.EarthLocation` as arguments and return a value
            that will be used by the `lqs_func` to evaluate the condition. If `None`, the `lqs_func` function will
            be used directly.

        lqs_func : `function`, default : `None`
            The function to convert the output of the `func` into a linear quality score between `0` and `1`.
            This function should take the output of the `func` and return a value between `0` and `1` that represents
            the quality of the condition. If `None`, the output of the `func` will be used directly.

        weight : `float`, default : 1
            The weight of this condition relative to other conditions. This value is used by the `~pyscope.telrun.Optimizer`
            inside the `~pyscope.telrun.Scheduler` to compute the overall quality of a `~pyscope.telrun.Field` or
            or `~pyscope.telrun.ScheduleBlock` based on the conditions that are evaluated. The weight should be a positive value,
            and the relative weight of each condition will be used to scale the output of the `lqs_func` function when computing the
            overall score. A weight of `0` will effectively disable the condition from being used in the optimization, and a
            weight of `1` is the default value. The weight can be set to any positive value to increase the relative importance of
            the condition. The composite linear quality score is typically computed as the geometric mean of the individual condition
            scores, so the weights are used to increase the power index of the geometric mean for each condition. Expressed
            mathematically:

            .. math::
                Q = \\left( \\prod_{i=1}^{N} q_i^{w_i} \\right)^{1 / \\sum_{i=1}^{N} w_i}

            where :math:`Q` is the composite quality score, :math:`q_i` is the quality score of the :math:`i`-th condition,
            and :math:`w_i` is the weight of the :math:`i`-th condition. The sum of the weights is used to normalize the
            composite quality score to a value between `0` and `1`. The default weight of `1` is used to give equal weight to
            all conditions, but users can adjust the weights to prioritize certain conditions over others. Since the weights
            are used as exponents in the geometric mean, `float` weights are possible.

        **kwargs : `dict`, default : {}
            Additional keyword arguments to pass to the condition functions for evaluation.


        See Also
        --------
        pyscope.telrun.CoordinateCondition
        pyscope.telrun.HourAngleCondition
        pyscope.telrun.AirmassCondition
        pyscope.telrun.MoonCondition
        pyscope.telrun.SunCondition
        pyscope.telrun.TimeCondition
        pyscope.telrun.SNRCondition

        """
        logger.debug(
            "BoundaryCondition(func=%s, lqs_func=%s, weight=%s)"
            % (func, lqs_func, weight)
        )

        if not callable(func) and not callable(lqs_func):
            raise ValueError("Either func or lqs_func must be provided.")
        self._func = func
        self._lqs_func = lqs_func
        self._weight = float(weight)
        self._kwargs = kwargs

    def __str__(self):
        """
        Return a `str` representation of the `~pyscope.telrun.BoundaryCondition`.

        Returns
        -------
        `str`
            A `str` representation of the `~pyscope.telrun.BoundaryCondition`.
        """
        logger.debug("BoundaryCondition().__str__() = %s" % self)

    def __repr__(self):
        """
        Return a `str` representation of the `~pyscope.telrun.BoundaryCondition`.

        Returns
        -------
        `str`
            A `str` representation of the `~pyscope.telrun.BoundaryCondition`.

        """
        logger.debug("BoundaryCondition().__repr__()")
        return str(self)

    def __call__(self, target, time, location, **kwargs):
        """
        Evaluate the `~pyscope.telrun.BoundaryCondition` for a given target, time, and location.

        This is a shortcut for calling the `func` and `lqs_func` functions directly. The `func` function
        evaluates the condition for the target, time, and location and returns a value that is then passed
        to the `lqs_func` function to convert the value into a linear quality score between `0` and `1`. The
        `lqs_func` function is optional, and if not provided, the output of the `func` function will be used
        directly as the quality score. The code is essentially equivalent to:

        .. code-block:: python

            if func is not None and lqs_func is None:
                value = func(target, time, location, **kwargs)
            elif lqs_func is not None:
                value = lqs_func(func(target, time, location, **kwargs), **kwargs)
            else:
                raise ValueError("Either func or lqs_func must be provided.")

        The `**kwargs` are passed to both the `func` and `lqs_func` functions as additional arguments. This is
        used in some subclasses (such as the `~pyscope.telrun.SNRCondition`) to pass additional parameters (such as
        an `~pyscope.observatory.Observatory`) to the `func` and `lqs_func` functions for evaluation.

        Parameters
        ----------
        target : `~astropy.coordinates.SkyCoord`
            The target field to observe.

        time : `~astropy.time.Time`
            The time of the observation.

        location : `~astropy.coordinates.EarthLocation`
            The location of the observatory.

        **kwargs : dict

        Returns
        -------
        `float`
            A `float` value between `0` and `1` that represents the linear quality score of the condition.

        """
        logger.debug(
            "BoundaryCondition().__call__(target=%s, time=%s, location=%s, kwargs=%s)"
            % (target, time, location, kwargs)
        )
        if kwargs is None:
            kwargs = self._kwargs

        if self._func is not None and self._lqs_func is None:
            value = self.calculate(target, time, location, **kwargs)
        elif self._lqs_func is not None:
            value = self.score(
                self.calculate(target, time, location, **kwargs), **kwargs
            )
        else:
            raise ValueError("Either func or lqs_func must be provided.")

        return value

    def calculate(target, time, location, **kwargs):
        return self._func(target, time, location, **kwargs)

    def score(value, **kwargs):
        return self._lqs_func(value, **kwargs)

    @property
    def weight(self):
        """
        The weight of this condition relative to other conditions.

        The weight can be set to any positive value to increase the relative importance of the condition. The composite
        linear quality score is typically computed as the geometric mean of the individual condition scores, so the weights
        are used to increase the power index of the geometric mean for each condition. Expressed mathematically:

        .. math::

            Q = \\left( \\prod_{i=1}^{N} q_i^{w_i} \\right)^{1 / \\sum_{i=1}^{N} w_i}

        where :math:`Q` is the composite quality score, :math:`q_i` is the quality score of the :math:`i`-th condition,
        and :math:`w_i` is the weight of the :math:`i`-th condition.
        """
        logger.debug("BoundaryCondition().weight == %s" % self._weight)
        return self._weight

    @property
    def kwargs(self):
        """
        Additional keyword arguments to pass to the condition functions for evaluation.
        """
        logger.debug("BoundaryCondition().kwargs == %s" % self._kwargs)
        return self._kwargs
