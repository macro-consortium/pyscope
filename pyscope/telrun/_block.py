import ast
import logging
from uuid import UUID, uuid4

from astropy.time import Time

from .configuration import Configuration
from .observer import Observer

logger = logging.getLogger(__name__)


class _Block:
    def __init__(self, config, observer, name="", description="", **kwargs):
        """
        A class to represent a time range in the schedule.

        A `~pyscope.telrun._Block` are used to represent a time range in the schedule. A `~pyscope.telrun._Block` can be
        used to represent allocated time with a `~pyscope.telrun.ScheduleBlock` or unallocated time with a
        `~pyscope.telrun.UnallocatedBlock`. The `~pyscope.telrun._Block` class is a base class that should not be instantiated
        directly. Instead, use the `~pyscope.telrun.ScheduleBlock` or `~pyscope.telrun.UnallocatedBlock` subclasses.

        Parameters
        ----------
        configuration : `~pyscope.telrun.Configuration`, required
            The `~pyscope.telrun.Configuration` to use for the `~pyscope.telrun._Block`. This `~pyscope.telrun.Configuration` will be
            used to set the telescope's `~pyscope.telrun.Configuration` at the start of the `~pyscope.telrun._Block` and
            will act as the default `~pyscope.telrun.Configuration` for all `~pyscope.telrun.Field` objects in the
            `~pyscope.telrun._Block` if a `~pyscope.telrun.Configuration` has not been provided. If a `~pyscope.telrun.Field`
            has a different `~pyscope.telrun.Configuration`, it will override the block `~pyscope.telrun.Configuration` for the
            duration of the `~pyscope.telrun.Field`.

        observer : `~pyscope.telrun.Observer`, required
            Associate this `~pyscope.telrun._Block` with an `~pyscope.telrun.Observer`. The `~pyscope.telrun.Observer` is a
            bookkeeping object for an `~pyscope.observatory.Observatory` with multiple users/user groups.

        name : `str`, default : ""
            A user-defined name for the `~pyscope.telrun._Block`. This parameter does not change
            the behavior of the `~pyscope.telrun._Block`, but it can be useful for identifying the
            `~pyscope.telrun._Block` in a schedule.

        description : `str`, default : ""
            A user-defined description for the `~pyscope.telrun._Block`. Similar to the `name`
            parameter, this parameter does not change the behavior of the `~pyscope.telrun._Block`.

        **kwargs : `dict`, default : {}
            A dictionary of keyword arguments that can be used to store additional information
            about the `~pyscope.telrun._Block`. This information can be used to store any additional
            information that is not covered by the `configuration`, `name`, or `description` parameters.

        See Also
        --------
        pyscope.telrun.ScheduleBlock : A subclass of `~pyscope.telrun._Block` that is used to schedule `~pyscope.telrun.Field` objects
            in a `~pyscope.telrun.Schedule`.
        pyscope.telrun.UnallocatedBlock : A subclass of `~pyscope.telrun._Block` that is used to represent unallocated time in a
            `~pyscope.telrun.Schedule`.
        pyscope.telrun.Configuration : A class that represents the configuration of the telescope.
        pyscope.telrun.Field : A class that represents a field to observe.
        """
        logger.debug(
            "_Block(config=%s, observer=%s, name=%s, description=%s, **kwargs=%s)"
            % (config, observer, name, description, kwargs)
        )
        self.config = config
        self.observer = observer
        self.name = name
        self.description = description
        self.kwargs = kwargs
        self._uuid = uuid4()
        self._start_time = None
        self._end_time = None

        logger.debug("_Block() = %s" % self)

    @classmethod
    def from_string(
        cls, string, config=None, observer=None, name="", description="", **kwargs
    ):
        """
        Create a new `~pyscope.telrun._Block` from a string representation. Additional arguments can be provided to override
        the parsed values.

        Parameters
        ----------
        string : `str`

        config : `~pyscope.telrun.Configuration`, default: `None`

        observer : `~pyscope.telrun.Observer`, default: `None`

        name : `str`, default : ""

        description : `str`, default : ""

        kwargs : `dict`, default : {}

        Returns
        -------
        block : `~pyscope.telrun._Block`

        """
        logger.debug(
            "_Block.from_string(string=%s, config=%s, name=%s, description=%s, **kwargs=%s)"
            % (string, config, name, description, kwargs)
        )

        # Parse the string representation to extract the block information
        block_info = string.split(
            "\n******************** Start Block Metadata ********************"
        )[1].split("\n******************** End Block Metadata ********************")[0]

        block_id = UUID(block_info.split("\nBlock ID: ")[1].split("\n")[0])
        name = block_info.split("\nName: ")[1].split("\n")[0] if name is "" else name
        description = (
            block_info.split("\nDescription: ")[1].split("\n")[0]
            if description is ""
            else description
        )
        kwargs = (
            ast.literal_eval(
                block_info.split("\nKeyword Arguments: ")[1].split("\n")[0]
            )
            if kwargs is {}
            else kwargs
        )
        start_time = (
            Time(block_info.split("\nStart Time: ")[1].split("\n")[0])
            if block_info.split("\nStart Time: ")[1].split("\n")[0] != "None"
            else None
        )
        end_time = (
            Time(block_info.split("\nEnd Time: ")[1].split("\n")[0])
            if block_info.split("\nEnd Time: ")[1].split("\n")[0] != "None"
            else None
        )
        observer = Observer.from_string(
            block_info.split("\nObserver: ")[1].split("\n")[0]
        )
        config = (
            Configuration.from_string(block_info.split("\nConfiguration: ")[1])
            if config is None
            else config
        )

        block = cls(
            config=config,
            observer=observer,
            name=name,
            description=description,
            **kwargs
        )
        block._uuid = block_id
        block._start_time = start_time
        block._end_time = end_time
        logger.debug("block=%s" % block)
        return block

    def __str__(self):
        """
        A `str` representation of the `~pyscope.telrun._Block`.

        Returns
        -------
        str : `str`
        """
        logger.debug("_Block().__str__()")
        s = "\n******************** Start Block Metadata ********************"
        s += "\nBlock ID: %s" % self.ID.hex
        s += "\nName: %s" % self.name
        s += "\nDescription: %s" % self.description
        s += "\nKeyword Arguments: %s" % self.kwargs
        s += "\nStart Time: %s" % self.start_time
        s += "\nEnd Time: %s" % self.end_time
        s += "\nObserver: %s" % self.observer
        s += "\nConfiguration: %s" % self.config
        s += "\n******************** End Block Metadata ********************"
        logger.debug("_Block().__str__() = %s" % s)
        return s

    def __repr__(self):
        """
        A `str` representation of the `~pyscope.telrun._Block`.

        Returns
        -------
        repr : `str`
        """
        logger.debug("_Block().__repr__()")
        return str(self)

    @property
    def config(self):
        """
        The default `~pyscope.telrun.Configuration` for the `~pyscope.telrun._Block`.

        Returns
        -------
        config : `~pyscope.telrun.Configuration`
        """
        logger.debug("_Block().config == %s" % self._config)
        return self._config

    @config.setter
    def config(self, value):
        """
        The default `~pyscope.telrun.Configuration` for the `~pyscope.telrun._Block`.

        Parameters
        ----------
        value : `~pyscope.telrun.Configuration`
        """
        logger.debug("_Block().config = %s" % value)
        if (
            Configuration not in (config.__class__, *config.__class__.__bases__)
            and value is not None
        ):
            raise TypeError(
                "The config parameter must be a Configuration object (class=%s) or a subclass of Configuration (bases=%s), not a %s",
                Configuration.__class__,
                Configuration.__class__.__bases__,
                type(config),
            )
        self._config = value

    @property
    def observer(self):
        """
        The `~pyscope.telrun.Observer` associated with the `~pyscope.telrun._Block`.

        Returns
        -------
        observer : `~pyscope.telrun.Observer`
        """
        logger.debug("_Block().observer == %s" % self._observer)
        return self._observer

    @observer.setter
    def observer(self, value):
        """
        The `~pyscope.telrun.Observer` associated with the `~pyscope.telrun._Block`.

        Parameters
        ----------
        value : `~pyscope.telrun.Observer`
        """
        logger.debug("_Block().observer = %s" % value)
        if (
            Observer not in (observer.__class__, *observer.__class__.__bases__)
            and value is not None
        ):
            raise TypeError(
                "The observer parameter must be an Observer object (class=%s) or a subclass of Observer (bases=%s), not a %s",
                Observer.__class__,
                Observer.__class__.__bases__,
                type(observer),
            )
        self._observer = value

    @property
    def name(self):
        """
        A user-defined `str` name for the `~pyscope.telrun._Block`.

        Returns
        -------
        name : `str`

        """
        logger.debug("_Block().name == %s" % self._name)
        return self._name

    @name.setter
    def name(self, value):
        """
        A user-defined `str` name for the `~pyscope.telrun._Block`.

        Parameters
        ----------
        value : `str`
        """
        logger.debug("_Block().name = %s" % value)
        if type(value) is not str:
            raise TypeError(
                "The name parameter must be a string, not a %s", type(value)
            )
        self._name = value

    @property
    def description(self):
        """
        A user-defined `str` description for the `~pyscope.telrun._Block`.

        Returns
        -------
        description : `str`
        """
        logger.debug("_Block().description == %s" % self._description)
        return self._description

    @description.setter
    def description(self, value):
        """
        A user-defined `str` description for the `~pyscope.telrun._Block`.

        Parameters
        ----------
        value : `str`

        """
        logger.debug("_Block().description = %s" % value)
        if type(value) is not str:
            raise TypeError(
                "The description parameter must be a string, not a %s", type(value)
            )
        self._description = value

    @property
    def kwargs(self):
        """
        Additional user-defined keyword arguments in a `dict` for the `~pyscope.telrun._Block`.

        Returns
        -------
        kwargs : `dict`

        """
        logger.debug("_Block().kwargs == %s" % self._kwargs)
        return self._kwargs

    @kwargs.setter
    def kwargs(self, value):
        """
        Additional user-defined keyword arguments for the `~pyscope.telrun._Block`.

        Parameters
        ----------
        value : `dict`

        """
        logger.debug("_Block().kwargs = %s" % value)
        if type(value) is not dict:
            raise TypeError(
                "The kwargs parameter must be a dict, not a %s", type(value)
            )
        self._kwargs = value

    @property
    def ID(self):
        """
        A `~uuid.UUID` that uniquely identifies the `~pyscope.telrun._Block`.

        Returns
        -------
        ID : `~uuid.UUID`
            The unique identifier for the `~pyscope.telrun._Block`.
        """
        logger.debug("_Block().ID == %s" % self._uuid)
        return self._uuid

    @property
    def start_time(self):
        """
        The `~astropy.time.Time` that represents the start of the `~pyscope.telrun._Block`.

        Returns
        -------
        start_time : `astropy.time.Time`
            The start time of the `~pyscope.telrun._Block`.
        """
        logger.debug("_Block().start_time == %s" % self._start_time)
        return self._start_time

    @property
    def end_time(self):
        """
        The `~astropy.time.Time` that represents the end of the `~pyscope.telrun._Block`.

        Returns
        -------
        end_time : `astropy.time.Time`
            The end time of the `~pyscope.telrun._Block`.
        """
        logger.debug("_Block().end_time == %s" % self._end_time)
        return self._end_time
