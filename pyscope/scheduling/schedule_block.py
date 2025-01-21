import logging

from .boundary_condition import BoundaryCondition
from .field import Field

logger = logging.getLogger(__name__)

logger.debug("ScheduleBlock imported")


class ScheduleBlock:
    def __init__(
        self,
        name="",  # Str
        description="",  # Str
        priority=0,  # Int
        observer=[],  # List(Observer)
        project=None,  # Project
        config=None,  # InstrumentConfiguration
        conditions=[],  # List(BoundaryCondition)
        fields=[],  # List(Field)
    ):
        """
        A class to contain a list of `~pyscope.scheduling.Field` objects to be scheduled as a single time range in the
        observing `~pyscope.scheduling.Schedule`.

        The `~pyscope.scheduling.ScheduleBlock` is the fundamental unit that users interact with when creating observing
        requests. It is a container for one or more `~pyscope.scheduling.Field` objects, which represent the actual
        observing targets. The `~pyscope.scheduling.ScheduleBlock` also contains metadata about the block used by the
        `~pyscope.scheduling.Scheduler` to determine the best possible schedule using the `~pyscope.scheduling.BoundaryCondition`
        objects and the priority level provided when instantiating the `~pyscope.scheduling.ScheduleBlock`.

        The `~pyscope.scheduling.Scheduler` can also take advantage of the `~pyscope.scheduling.Field` objects themselves to make
        scheduling decisions. This mode is optimal for a `~pyscope.scheduling.ScheduleBlock` that contains only one
        `~pyscope.scheduling.Field` or multiple `~pyscope.scheduling.Field` objects that have small angular separations on the
        sky. For larger separations, it is recommended to create separate `~pyscope.scheduling.ScheduleBlock` objects for
        each `~pyscope.scheduling.Field`.

        Parameters
        ----------
        name : `str`, default : ""
            A user-defined name for the `~pyscope.scheduling.ScheduleBlock`. This parameter does not change
            the behavior of the `~pyscope.scheduling.ScheduleBlock`, but it can be useful for identifying the
            `~pyscope.scheduling.ScheduleBlock` in a schedule.

        description : `str`, default : ""
            A user-defined description for the `~pyscope.scheduling.ScheduleBlock`. Similar to the `name`
            parameter, this parameter does not change the behavior of the `~pyscope.scheduling.ScheduleBlock`.

        priority : `int`, default : 0
            The priority level of the `~pyscope.scheduling.ScheduleBlock`. The `~pyscope.scheduling.Prioritizer` inside the
            `~pyscope.scheduling.Scheduler` will use this parameter to determine the best possible schedule. The highest
            priority level is 1 and decreasing priority levels are integers above 1. The lowest priority is 0, which
            is the default value. Tiebreakers are usually determined by the `~pyscope.scheduling.Prioritizer` inside the
            `~pyscope.scheduling.Scheduler`, but some more advanced scheduling algorithms may use results from the
            `~pyscope.scheduling.Optimizer` to break ties.

        observer : `list` of `~pyscope.scheduling.Observer`, default : []
            The `~pyscope.scheduling.Observer` objects to assign this `~pyscope.scheduling.ScheduleBlock` to. This parameter
            is useful for tracking which observers are responsible for the `~pyscope.scheduling.ScheduleBlock` and for
            generating reports for the observers. The `~pyscope.scheduling.ScheduleBlock` can be assigned to multiple
            observers or no observers if desiered. This parameter does not change the behavior of the
            `~pyscope.scheduling.ScheduleBlock`.

        project : `~pyscope.scheduling.Project`, default : `None`
            The `~pyscope.scheduling.Project` object to assign this `~pyscope.scheduling.ScheduleBlock` to. This parameter
            does not change the behavior of the `~pyscope.scheduling.ScheduleBlock`, but it can be useful for tracking
            which project the `~pyscope.scheduling.ScheduleBlock` is associated with and for generating reports for the
            project. Each `~pyscope.scheduling.ScheduleBlock` can only be assigned to one `~pyscope.scheduling.Project`.

        config : `~pyscope.telrun.InstrumentConfiguration`, default : `None`
            The `~pyscope.telrun.InstrumentConfiguration` to use for the `~pyscope.scheduling.ScheduleBlock`. This `~pyscope.telrun.InstrumentConfiguration` will be
            used to set the telescope's `~pyscope.telrun.InstrumentConfiguration` at the start of the `~pyscope.scheduling.ScheduleBlock` and
            will act as the default `~pyscope.telrun.InstrumentConfiguration` for all `~pyscope.scheduling.Field` objects in the
            `~pyscope.scheduling.ScheduleBlock` if a `~pyscope.telrun.InstrumentConfiguration` has not been provided within the
            `~pyscope.scheduling.Field`. If a `~pyscope.scheduling.Field` has a different `~pyscope.telrun.InstrumentConfiguration`,
            it will override the block `~pyscope.telrun.InstrumentConfiguration` for the duration of the `~pyscope.scheduling.Field`.

        conditions : `list` of `~pyscope.scheduling.BoundaryCondition`, default : []
            A list of `~pyscope.scheduling.BoundaryCondition` objects that define the constraints for all `~pyscope.scheduling.Field`
            objects in the `~pyscope.scheduling.ScheduleBlock`. The `~pyscope.telrun.Optimizer` inside the `~pyscope.scheduling.Scheduler`
            will use the `~pyscope.scheduling.BoundaryCondition` objects to determine the best possible schedule.

        fields : `list` of `~pyscope.scheduling.Field`, default : []
            A list of `~pyscope.scheduling.Field` objects to be scheduled in the `~pyscope.scheduling.ScheduleBlock`. The
            `~pyscope.scheduling.Field` objects will be executed in the order they are provided in the list. If the
            `~pyscope.scheduling.Field` objects have different `~pyscope.telrun.InstrumentConfiguration` objects, the `~pyscope.telrun.InstrumentConfiguration`
            object for the `~pyscope.scheduling.Field` will override the block `~pyscope.telrun.InstrumentConfiguration` for the duration
            of the `~pyscope.scheduling.Field`.

        """
        logger.debug(
            """ScheduleBlock(
                name=%s,
                description=%s,
                priority=%i,
                observer=%s,
                project=%s,
                config=%s,
                conditions=%s,
                fields=%s,
            )"""
            % (
                name,
                description,
                priority,
                observer,
                project,
                config,
                conditions,
                fields,
            )
        )

        super().__init__(
            config=config,
            observer=observer,
            name=name,
            description=description,
            **kwargs,
        )

        self.project_code = project_code
        self.conditions = conditions
        self.priority = priority
        self.fields = fields
        logger.debug("ScheduleBlock() = %s" % self)

    @classmethod
    def from_string(
        cls,
        string,
        config=None,
        observer=None,
        name="",
        description="",
        project_code="",
        conditions=[],
        priority=0,
        fields=[],
        **kwargs
    ):
        """
        Create a new (list of) `~pyscope.scheduling.ScheduleBlock` object(s) from a string representation.

        Parameters
        ----------
        string : `str`, required

        config : `~pyscope.telrun.InstrumentConfiguration`, default : `None`

        observer : `~pyscope.telrun.Observer`, default : `None`

        name : `str`, default : ""

        description : `str`, default : ""

        project_code : `str`, default : ""

        conditions : `list` of `~pyscope.scheduling.BoundaryCondition`, default : []

        priority : `int`, default : 0

        fields : `list` of `~pyscope.scheduling.Field`, default : []

        **kwargs : `dict`, default : {}

        Returns
        -------
        `~pyscope.scheduling.ScheduleBlock` or `list` of `~pyscope.scheduling.ScheduleBlock`

        """
        logger.debug(
            "ScheduleBlock.from_string(string=%s, config=%s, name=%s, description=%s, conditions=%s, priority=%s, fields=%s, **kwargs=%s)"
            % (
                string,
                config,
                name,
                description,
                conditions,
                priority,
                fields,
                kwargs,
            )
        )

        n_blocks = string.count(
            "******************** Start ScheduleBlock ********************"
        )
        end_blocks = string.count(
            "******************** End ScheduleBlock ********************"
        )
        if end_blocks != n_blocks:
            raise ValueError(
                "Invalid string representation of ScheduleBlock, %s start blocks and %s end blocks"
                % (n_blocks, end_blocks)
            )
        logger.debug("n_blocks=%i" % n_blocks)
        sbs = []
        for i in range(n_blocks):
            logger.debug("Start i=%i" % i)
            block_info = string.split(
                "\n******************** Start ScheduleBlock ********************"
            )[i + 1].split(
                "\n******************** End ScheduleBlock ********************"
            )[
                0
            ]
            logger.debug("block_info=%s" % block_info)

            block = super().from_string(
                block_info,
                config=config,
                observer=observer,
                name=name,
                description=description,
                **kwargs,
            )
            logger.debug("block=%s" % block)

            priority = int(block_info.split("\nPriority: ")[1].split("\n")[0])
            logger.debug("priority=%i" % priority)

            project_code = block_info.split("\nProject Code: ")[1].split("\n")[
                0
            ]

            conditions_info = block_info.split(
                "\n********** Start Conditions **********"
            )[1].split("\n********** End Conditions **********")[0]
            n_conditions = conditions_info.count(
                "******************** Start BoundaryCondition ********************"
            )
            end_conditions = conditions_info.count(
                "******************** End BoundaryCondition ********************"
            )
            if end_conditions != n_conditions:
                raise ValueError(
                    "Invalid string representation of BoundaryCondition, %s start blocks and %s end blocks"
                    % (n_conditions, end_conditions)
                )
            logger.debug("n_conditions=%i" % n_conditions)
            conditions = []
            for j in range(n_conditions):
                logger.debug("Start j=%i" % j)
                condition_info = conditions_info.split(
                    "\n******************** Start BoundaryCondition ********************"
                )[j + 1].split(
                    "\n******************** End BoundaryCondition ********************"
                )[
                    0
                ]
                logger.debug("condition_info=%s" % condition_info)
                condition_type = condition_info.split("\nType: ")[1].split(
                    "\n"
                )[0]
                condition_kwargs = ast.literal_eval(
                    condition_info.split("\nType: %s\n" % condition_type)[1]
                )
                try:
                    condition_class = getattr(
                        sys.modules[__name__], condition_type
                    )
                except BaseException:
                    try:
                        module_name = (
                            condition_kwargs.values()[0]
                            .split("/")[-1]
                            .split(".")[0]
                        )
                        spec = importlib.util.spec_from_file_location(
                            module_name, condition_kwargs[0]
                        )
                        module = importlib.util.module_from_spec(spec)
                        sys.modules[module_name] = module
                        spec.loader.exec_module(module)
                        condition_class = getattr(module, condition_type)

                        if len(condition_kwargs) > 1:
                            condition_kwargs = condition_kwargs[1:]
                        else:
                            condition_kwargs = None
                    except BaseException:
                        return None

                if condition_kwargs is None:
                    condition = condition_class.from_string(condition_info)
                else:
                    condition = condition_class.from_string(
                        condition_info, **condition_kwargs
                    )

                conditions.append(condition)
                logger.debug("condition=%s" % condition)

            fields_info = block_info.split(
                "\n********** Start Fields **********"
            )[1].split("\n********** End Fields **********")[0]
            n_fields = fields_info.count(
                "******************** Start Field ********************"
            )
            end_fields = fields_info.count(
                "******************** End Field ********************"
            )
            if end_fields != n_fields:
                raise ValueError(
                    "Invalid string representation of Field, %s start blocks and %s end blocks"
                    % (n_fields, end_fields)
                )
            logger.debug("n_fields=%i" % n_fields)
            fields = []
            for j in range(n_fields):
                logger.debug("Start j=%i" % j)
                field_info = fields_info.split(
                    "\n******************** Start Field ********************"
                )[j + 1].split(
                    "\n******************** End Field ********************"
                )[
                    0
                ]
                logger.debug("field_info=%s" % field_info)
                field_type = field_info.split("\nType: ")[1].split("\n")[0]
                field_kwargs = ast.literal_eval(
                    field_info.split("\nType: %s\n" % field_type)[1]
                )
                try:
                    field_class = getattr(sys.modules[__name__], field_type)
                except BaseException:
                    try:
                        module_name = (
                            field_kwargs.values()[0]
                            .split("/")[-1]
                            .split(".")[0]
                        )
                        spec = importlib.util.spec_from_file_location(
                            module_name, field_kwargs[0]
                        )
                        module = importlib.util.module_from_spec(spec)
                        sys.modules[module_name] = module
                        spec.loader.exec_module(module)
                        field_class = getattr(module, field_type)

                        if len(field_kwargs) > 1:
                            field_kwargs = field_kwargs[1:]
                        else:
                            field_kwargs = None
                    except BaseException:
                        return None

                if field_kwargs is None:
                    field = field_class.from_string(field_info)
                else:
                    field = field_class.from_string(field_info, **field_kwargs)

                fields.append(field)
                logger.debug("field=%s" % field)

            sb = cls(
                config=block.config,
                observer=block.observer,
                name=block.name,
                description=block.description,
                project_code=project_code,
                conditions=conditions,
                priority=priority,
                fields=fields,
                **block.kwargs,
            )
            sb._uuid = block._uuid
            sb._start_time = block._start_time
            sb._end_time = block._end_time

            logger.debug("sb=%s" % sb)
            sbs.append(sb)
            logger.debug("End i=%i" % i)

        logger.debug("ScheduleBlock.from_string() = %s" % sbs)
        if len(sbs) == 1:
            return sbs[0]
        return sbs

    def __str__(self):
        """
        Return a string representation of the `~pyscope.scheduling.ScheduleBlock`.

        Returns
        -------
        `str`
            A string representation of the `~pyscope.scheduling.ScheduleBlock`.

        """
        logger.debug("ScheduleBlock().__str__()")
        s = "\n******************** Start ScheduleBlock ********************"
        s += super().__str__()
        s += "\nPriority: %i" % self.priority
        s += "\n********** Start Conditions **********"
        for condition in self.conditions:
            s += "\n" + str(condition)
        s += "\n********** End Conditions **********"
        s += "\n********** Start Fields **********"
        for field in self.fields:
            s += "\n" + str(field)
        s += "\n********** End Fields **********"
        s += "\n******************** End ScheduleBlock ********************"
        logger.debug("ScheduleBlock().__str__() = %s" % s)
        return s

    @property
    def conditions(self):
        """
        Get the list of `~pyscope.scheduling.BoundaryCondition` objects for the `~pyscope.scheduling.ScheduleBlock`.

        Returns
        -------
        `list` of `~pyscope.scheduling.BoundaryCondition`
            The list of `~pyscope.scheduling.BoundaryCondition` objects for the `~pyscope.scheduling.ScheduleBlock`.

        """
        logger.debug("ScheduleBlock().conditions == %s" % self._conditions)
        return self._conditions

    @conditions.setter
    def conditions(self, value):
        """
        Set the list of `~pyscope.scheduling.BoundaryCondition` objects for the `~pyscope.scheduling.ScheduleBlock`.

        Parameters
        ----------
        conditions : `list` of `~pyscope.scheduling.BoundaryCondition`
            The list of `~pyscope.scheduling.BoundaryCondition` objects for the `~pyscope.scheduling.ScheduleBlock`.

        """
        logger.debug("ScheduleBlock().conditions = %s" % value)

        if not isinstance(value, list):
            value = [value]

        for i, condition in enumerate(value):
            if BoundaryCondition not in (
                condition.__class__,
                *condition.__class__.__bases__,
            ):
                raise TypeError(
                    "conditions must be a list of BoundaryCondition objects. Got %s, %s instead for %s (number %i)"
                    % (
                        condition.__class__,
                        condition.__class__.__bases__,
                        condition,
                        i,
                    )
                )

        self._conditions = value

    @property
    def priority(self):
        """
        Get the priority level of the `~pyscope.scheduling.ScheduleBlock`.

        Returns
        -------
        `int`
            The priority level of the `~pyscope.scheduling.ScheduleBlock`.

        """
        logger.debug("ScheduleBlock().priority == %i" % self._priority)
        return self._priority

    @priority.setter
    def priority(self, value):
        """
        Set the priority level of the `~pyscope.scheduling.ScheduleBlock`.

        Parameters
        ----------
        priority : `int`
            The priority level of the `~pyscope.scheduling.ScheduleBlock`.

        """
        logger.debug("ScheduleBlock().priority = %i" % value)
        self._priority = int(value)

    @property
    def fields(self):
        """
        Get the list of `~pyscope.scheduling.Field` objects for the `~pyscope.scheduling.ScheduleBlock`.

        Returns
        -------
        `list` of `~pyscope.scheduling.Field`
            The list of `~pyscope.scheduling.Field` objects for the `~pyscope.scheduling.ScheduleBlock`.

        """
        logger.debug("ScheduleBlock().fields == %s" % self._fields)
        return self._fields

    @fields.setter
    def fields(self, value):
        """
        Set the list of `~pyscope.scheduling.Field` objects for the `~pyscope.scheduling.ScheduleBlock`.

        Parameters
        ----------
        fields : `list` of `~pyscope.scheduling.Field`
            The list of `~pyscope.scheduling.Field` objects for the `~pyscope.scheduling.ScheduleBlock`.

        """
        logger.debug("ScheduleBlock().fields = %s" % value)

        if not isinstance(value, list):
            value = [value]

        for i, field in enumerate(value):
            if Field not in (field.__class__, *field.__class__.__bases__):
                raise TypeError(
                    "fields must be a list of Field objects. Got %s, %s instead for %s (number %i)"
                    % (field.__class__, field.__class__.__bases__, field, i)
                )

        self._fields = value
