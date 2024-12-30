import logging

from ._block import _Block
from .boundary_condition import BoundaryCondition
from .field import Field

logger = logging.getLogger(__name__)


class ScheduleBlock(_Block):
    def __init__(
        self,
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
        A class to contain a list of `~pyscope.telrun.Field` objects to be scheduled as a single time range in the
        observing `~pyscope.telrun.Schedule`.

        The `~pyscope.telrun.ScheduleBlock` is the fundamental unit that users interact with when creating observing
        requests. It is a container for one or more `~pyscope.telrun.Field` objects, which represent the actual
        observing targets. The `~pyscope.telrun.ScheduleBlock` also contains metadata about the block used by the
        `~pyscope.telrun.Scheduler` to determine the best possible schedule using the `~pyscope.telrun.BoundaryCondition`
        objects and the priority level provided when instantiating the `~pyscope.telrun.ScheduleBlock`.

        The `~pyscope.telrun.Scheduler` can also take advantage of the `~pyscope.telrun.Field` objects themselves to make
        scheduling decisions. This mode is optimal for a `~pyscope.telrun.ScheduleBlock` that contains only one
        `~pyscope.telrun.Field` or multiple `~pyscope.telrun.Field` objects that have small angular separations on the
        sky. For larger separations, it is recommended to create separate `~pyscope.telrun.ScheduleBlock` objects for
        each `~pyscope.telrun.Field` if the indexing of the `~pyscope.telrun.Field` objects is *not* important. If the order
        of the `~pyscope.telrun.Field` objects *is* important, then we recommend the user employs a single
        `~pyscope.telrun.ScheduleBlock` with a user-defined `~pyscope.telrun.BoundaryCondition` that will restrict the valid
        local sidereal time (LST) range for the start of the `~pyscope.telrun.ScheduleBlock` to ensure that the
        `~pyscope.telrun.ScheduleBlock` is executed at the most optimal time when using a basic `~pyscope.telrun.Scheduler`
        (more advanced scheduling algorithms may not require this).

        Parameters
        ----------
        config : `~pyscope.telrun.Configuration`, default : `None`
            The `~pyscope.telrun.Configuration` to use for the `~pyscope.telrun.ScheduleBlock`. This `~pyscope.telrun.Configuration` will be
            used to set the telescope's `~pyscope.telrun.Configuration` at the start of the `~pyscope.telrun.ScheduleBlock` and
            will act as the default `~pyscope.telrun.Configuration` for all `~pyscope.telrun.Field` objects in the
            `~pyscope.telrun.ScheduleBlock` if a `~pyscope.telrun.Configuration` has not been provided. If a `~pyscope.telrun.Field`
            has a different `~pyscope.telrun.Configuration`, it will override the block `~pyscope.telrun.Configuration` for the
            duration of the `~pyscope.telrun.Field`.

        observer : `~pyscope.telrun.Observer`, default : `None`
            The `~pyscope.telrun.Observer` to use for the `~pyscope.telrun.ScheduleBlock`.

        name : `str`, default : ""
            A user-defined name for the `~pyscope.telrun.ScheduleBlock`. This parameter does not change
            the behavior of the `~pyscope.telrun.ScheduleBlock`, but it can be useful for identifying the
            `~pyscope.telrun.ScheduleBlock` in a schedule.

        description : `str`, default : ""
            A user-defined description for the `~pyscope.telrun.ScheduleBlock`. Similar to the `name`
            parameter, this parameter does not change the behavior of the `~pyscope.telrun.ScheduleBlock`.

        project_code : `str`, default : ""
            A user-defined project code for the `~pyscope.telrun.ScheduleBlock`. This parameter does not change
            the behavior of the `~pyscope.telrun.ScheduleBlock`, but it can be useful for identifying the
            `~pyscope.telrun.ScheduleBlock`.

        conditions : `list` of `~pyscope.telrun.BoundaryCondition`, default : []
            A list of `~pyscope.telrun.BoundaryCondition` objects that define the constraints for all `~pyscope.telrun.Field`
            objects in the `~pyscope.telrun.ScheduleBlock`. The `~pyscope.telrun.Optimizer` inside the `~pyscope.telrun.Scheduler`
            will use the `~pyscope.telrun.BoundaryCondition` objects to determine the best possible schedule.

        priority : `int`, default : 0
            The priority level of the `~pyscope.telrun.ScheduleBlock`. The `~pyscope.telrun.Prioritizer` inside the
            `~pyscope.telrun.Scheduler` will use this parameter to determine the best possible schedule. The highest
            priority level is 1 and decreasing priority levels are integers above 1. The lowest priority is 0, which
            is the default value. Tiebreakers are usually determined by the `~pyscope.telrun.Prioritizer` inside the
            `~pyscope.telrun.Scheduler`, but some more advanced scheduling algorithms may use results from the
            `~pyscope.telrun.Optimizer` to break ties.

        fields : `list` of `~pyscope.telrun.Field`, default : []
            A list of `~pyscope.telrun.Field` objects to be scheduled in the `~pyscope.telrun.ScheduleBlock`. The
            `~pyscope.telrun.Field` objects will be executed in the order they are provided in the list. If the
            `~pyscope.telrun.Field` objects have different `~pyscope.telrun.Configuration` objects, the `~pyscope.telrun.Configuration`
            object for the `~pyscope.telrun.Field` will override the block `~pyscope.telrun.Configuration` for the duration
            of the `~pyscope.telrun.Field`.

        **kwargs : `dict`, default : {}
            A dictionary of keyword arguments that can be used to store additional information
            about the `~pyscope.telrun.ScheduleBlock`. This information can be used to store any additional
            information that is not covered by the `config`, `name`, or `description` parameters.

        """
        logger.debug(
            "ScheduleBlock(config=%s, observer=%s, name=%s, description=%s, conditions=%s, priority=%s, fields=%s, **kwargs=%s)"
            % (
                config,
                observer,
                name,
                description,
                conditions,
                priority,
                fields,
                kwargs,
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
        Create a new (list of) `~pyscope.telrun.ScheduleBlock` object(s) from a string representation.

        Parameters
        ----------
        string : `str`, required

        config : `~pyscope.telrun.Configuration`, default : `None`

        observer : `~pyscope.telrun.Observer`, default : `None`

        name : `str`, default : ""

        description : `str`, default : ""

        project_code : `str`, default : ""

        conditions : `list` of `~pyscope.telrun.BoundaryCondition`, default : []

        priority : `int`, default : 0

        fields : `list` of `~pyscope.telrun.Field`, default : []

        **kwargs : `dict`, default : {}

        Returns
        -------
        `~pyscope.telrun.ScheduleBlock` or `list` of `~pyscope.telrun.ScheduleBlock`

        """
        logger.debug(
            "ScheduleBlock.from_string(string=%s, config=%s, name=%s, description=%s, conditions=%s, priority=%s, fields=%s, **kwargs=%s)"
            % (string, config, name, description, conditions, priority, fields, kwargs)
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

            project_code = block_info.split("\nProject Code: ")[1].split("\n")[0]

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
                condition_type = condition_info.split("\nType: ")[1].split("\n")[0]
                condition_kwargs = ast.literal_eval(
                    condition_info.split("\nType: %s\n" % condition_type)[1]
                )
                try:
                    condition_class = getattr(sys.modules[__name__], condition_type)
                except:
                    try:
                        module_name = (
                            condition_kwargs.values()[0].split("/")[-1].split(".")[0]
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
                    except:
                        return None

                if condition_kwargs is None:
                    condition = condition_class.from_string(condition_info)
                else:
                    condition = condition_class.from_string(
                        condition_info, **condition_kwargs
                    )

                conditions.append(condition)
                logger.debug("condition=%s" % condition)

            fields_info = block_info.split("\n********** Start Fields **********")[
                1
            ].split("\n********** End Fields **********")[0]
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
                )[j + 1].split("\n******************** End Field ********************")[
                    0
                ]
                logger.debug("field_info=%s" % field_info)
                field_type = field_info.split("\nType: ")[1].split("\n")[0]
                field_kwargs = ast.literal_eval(
                    field_info.split("\nType: %s\n" % field_type)[1]
                )
                try:
                    field_class = getattr(sys.modules[__name__], field_type)
                except:
                    try:
                        module_name = (
                            field_kwargs.values()[0].split("/")[-1].split(".")[0]
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
                    except:
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
        Return a string representation of the `~pyscope.telrun.ScheduleBlock`.

        Returns
        -------
        `str`
            A string representation of the `~pyscope.telrun.ScheduleBlock`.

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
        Get the list of `~pyscope.telrun.BoundaryCondition` objects for the `~pyscope.telrun.ScheduleBlock`.

        Returns
        -------
        `list` of `~pyscope.telrun.BoundaryCondition`
            The list of `~pyscope.telrun.BoundaryCondition` objects for the `~pyscope.telrun.ScheduleBlock`.

        """
        logger.debug("ScheduleBlock().conditions == %s" % self._conditions)
        return self._conditions

    @conditions.setter
    def conditions(self, value):
        """
        Set the list of `~pyscope.telrun.BoundaryCondition` objects for the `~pyscope.telrun.ScheduleBlock`.

        Parameters
        ----------
        conditions : `list` of `~pyscope.telrun.BoundaryCondition`
            The list of `~pyscope.telrun.BoundaryCondition` objects for the `~pyscope.telrun.ScheduleBlock`.

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
                    % (condition.__class__, condition.__class__.__bases__, condition, i)
                )

        self._conditions = value

    @property
    def priority(self):
        """
        Get the priority level of the `~pyscope.telrun.ScheduleBlock`.

        Returns
        -------
        `int`
            The priority level of the `~pyscope.telrun.ScheduleBlock`.

        """
        logger.debug("ScheduleBlock().priority == %i" % self._priority)
        return self._priority

    @priority.setter
    def priority(self, value):
        """
        Set the priority level of the `~pyscope.telrun.ScheduleBlock`.

        Parameters
        ----------
        priority : `int`
            The priority level of the `~pyscope.telrun.ScheduleBlock`.

        """
        logger.debug("ScheduleBlock().priority = %i" % value)
        self._priority = int(value)

    @property
    def fields(self):
        """
        Get the list of `~pyscope.telrun.Field` objects for the `~pyscope.telrun.ScheduleBlock`.

        Returns
        -------
        `list` of `~pyscope.telrun.Field`
            The list of `~pyscope.telrun.Field` objects for the `~pyscope.telrun.ScheduleBlock`.

        """
        logger.debug("ScheduleBlock().fields == %s" % self._fields)
        return self._fields

    @fields.setter
    def fields(self, value):
        """
        Set the list of `~pyscope.telrun.Field` objects for the `~pyscope.telrun.ScheduleBlock`.

        Parameters
        ----------
        fields : `list` of `~pyscope.telrun.Field`
            The list of `~pyscope.telrun.Field` objects for the `~pyscope.telrun.ScheduleBlock`.

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
