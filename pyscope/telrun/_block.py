import ast
import logging
from uuid import UUID, uuid4

from astropy.time import Time

from .configuration import Configuration

logger = logging.getLogger(__name__)


class _Block:
    def __init__(self, *args, config=None, name=None, description=None, **kwargs):
        """
        A class to represent a time range in the schedule.

        A `~pyscope.telrun._Block` are used to represent a time range in the schedule. A `~pyscope.telrun._Block` can be
        used to represent allocated time with a `~pyscope.telrun.ScheduleBlock` or unallocated time with a
        `~pyscope.telrun.UnallocatedBlock`. The `~pyscope.telrun._Block` class is a base class that should not be instantiated
        directly. Instead, use the `~pyscope.telrun.ScheduleBlock` or `~pyscope.telrun.UnallocatedBlock` subclasses.

        Parameters
        ----------
        *args : `tuple`
            If provided, the first argument should be a string representation of a `~pyscope.telrun._Block`. The `from_string`
            class method will parse the string representation and create a new `~pyscope.telrun._Block` object. The remaining
            arguments will override the parsed values.

        configuration : `~pyscope.telrun.Configuration`, default: `None`
            The `~pyscope.telrun.Configuration` to use for the `~pyscope.telrun._Block`. This `~pyscope.telrun.Configuration` will be
            used to set the telescope's `~pyscope.telrun.Configuration` at the start of the `~pyscope.telrun._Block` and
            will act as the default `~pyscope.telrun.Configuration` for all `~pyscope.telrun.Field` s
            in the `~pyscope.telrun._Block` if a `~pyscope.telrun.Configuration` has not been provided. If a `~pyscope.telrun.Field`
            has a different `~pyscope.telrun.Configuration`, it will override the block `~pyscope.telrun.Configuration` for the
            duration of the `~pyscope.telrun.Field`.

        name : `str`, default: `None`
            A user-defined name for the `~pyscope.telrun._Block`. This parameter does not change
            the behavior of the `~pyscope.telrun._Block`, but it can be useful for identifying the
            `~pyscope.telrun._Block` in a schedule.

        description : `str`, default: `None`
            A user-defined description for the `~pyscope.telrun._Block`. Similar to the `name`
            parameter, this parameter does not change the behavior of the `~pyscope.telrun._Block`.

        kwargs : `dict`
            A dictionary of keyword arguments that can be used to store additional information
            about the `~pyscope.telrun._Block`. This information can be used to store any additional
            information that is not covered by the `configuration`, `name`, or `description` parameters.

        See Also
        --------
        pyscope.telrun.ScheduleBlock : A subclass of `~pyscope.telrun._Block` that is used to schedule `~pyscope.telrun.Field` s
            in a `~pyscope.telrun.Schedule`.
        pyscope.telrun.UnallocatedBlock : A subclass of `~pyscope.telrun._Block` that is used to represent unallocated time in a
            `~pyscope.telrun.Schedule`.
        pyscope.telrun.Configuration : A class that represents the configuration of the telescope.
        pyscope.telrun.Field : A class that represents a field to observe.
        """
        if len(args) > 0:
            self = self.from_string(
                args[0], config=config, name=name, description=description, **kwargs
            )
            return

        logger.debug(
            "\n\n\n----------------------------------------------------------------------"
        )
        logger.debug("Creating a new Block object...")
        logger.debug("configuration=%s" % config)
        logger.debug("name=%s" % name)
        logger.debug("description=%s" % description)
        logger.debug("kwargs=%s" % kwargs)

        if type(config) is not Configuration:
            logger.error(
                "The configuration parameter must be a Configuration object, not a %s",
                type(config),
            )
            logger.error("Creating a new empty Configuration object.")
            config = Configuration()

        self.config = config
        self.name = name
        self.description = description
        self.kwargs = kwargs

        self._uuid = uuid4()
        self._start_time = None
        self._end_time = None

        logger.debug("Block ID: %s" % self.ID.hex)
        logger.debug("Creating a new Block object... Done!")
        logger.debug(
            "----------------------------------------------------------------------\n\n\n"
        )

    @classmethod
    def from_string(cls, string, config=None, name=None, description=None, **kwargs):
        """
        Create a new `~pyscope.telrun._Block` from a string representation. Additional arguments can be provided to override
        the parsed values.

        Parameters
        ----------
        string : `str`

        config : `~pyscope.telrun.Configuration`, default: `None`

        name : `str`, default: `None`

        description : `str`, default: `None`

        kwargs : `dict`

        Returns
        -------
        block : `~pyscope.telrun._Block`

        """
        logger.debug("_Block.from_string called")
        logger.debug("Creating a new Block object from string...")
        logger.debug("string=%s" % string)

        # Parse the string representation to extract the block information
        block_info = string.split("\n")
        block_id = uuid(hex=block_info[1].split("Block ID: ")[1])
        if name is None:
            name = (
                block_info[2].split("Name: ")[1]
                if block_info[2].split("Name: ")[1] != "None"
                else None
            )
        if description is None:
            description = (
                block_info[3].split("Description: ")[1]
                if block_info[3].split("Description: ")[1] != "None"
                else None
            )

        if kwargs is None:
            try:
                kwargs = ast.literal_eval(block_info[4].split("Keyword Arguments: ")[1])
            except:
                logger.error("Failed to parse the keyword arguments.")
                kwargs = {}

        start_time = (
            Time(block_info[5].split("Start Time: ")[1])
            if block_info[5].split("Start Time: ")[1] != "None"
            else None
        )
        end_time = (
            Time(block_info[6].split("End Time: ")[1])
            if block_info[6].split("End Time: ")[1] != "None"
            else None
        )

        if config is None:
            config = (
                Configuration.from_string(block_info[7].split("Configuration: ")[1])
                if block_info[7].split("Configuration: ")[1] != "None"
                else None
            )

        # Create a new block object
        block = cls(config=config, name=name, description=description, **kwargs)
        block._uuid = block_id
        block._start_time = start_time
        block._end_time = end_time

        logger.debug("Creating a new Block object from string... Done!")
        return block

    def __str__(self):
        """
        A `str` representation of the `~pyscope.telrun._Block`.

        Returns
        -------
        str : `str`
        """
        logger.debug("_Block.__str__ called")
        s = "\nBlock ID: %s\n" % self.ID.hex
        s += "Name: %s\n" % self.name
        s += "Description: %s\n" % self.description
        s += "Keyword Arguments: %s\n" % self.kwargs
        s += "Start Time: %s\n" % self.start_time
        s += "End Time: %s\n" % self.end_time
        s += "Configuration: %s\n" % self.config
        return s

    def __repr__(self):
        """
        A `str` representation of the `~pyscope.telrun._Block`.

        Returns
        -------
        repr : `str`
        """
        logger.debug("_Block.__repr__ called")
        return str(self)

    @property
    def config(self):
        """
        The default `~pyscope.telrun.Configuration` for the `~pyscope.telrun._Block`.

        Returns
        -------
        config : `~pyscope.telrun.Configuration`
        """
        logger.debug("_Block.config called")
        return Configuration(self._config)

    @config.setter
    def config(self, value):
        """
        The default `~pyscope.telrun.Configuration` for the `~pyscope.telrun._Block`.

        Parameters
        ----------
        value : `~pyscope.telrun.Configuration`
        """
        logger.debug("_Block.config(value=%s) called" % value)
        if type(value) is not Configuration:
            logger.error(
                "The configuration parameter must be a Configuration object, not a %s",
                type(value),
            )
            logger.error("Ignoring the new configuration.")
            return
        logger.debug("Setting the configuration to %s" % value)
        self._config = value

    @property
    def name(self):
        """
        A user-defined `str` name for the `~pyscope.telrun._Block`.

        Returns
        -------
        name : `str`

        """
        logger.debug("_Block.name called")
        return str(self._name)

    @name.setter
    def name(self, value):
        """
        A user-defined `str` name for the `~pyscope.telrun._Block`.

        Parameters
        ----------
        value : `str`
        """
        logger.debug("_Block.name(value=%s) called" % value)
        if type(value) is not str:
            logger.error("The name parameter must be a string, not a %s", type(value))
            logger.error("Ignoring the new name.")
            return
        logger.debug("Setting the name to %s" % value)
        self._name = value

    @property
    def description(self):
        """
        A user-defined `str` description for the `~pyscope.telrun._Block`.

        Returns
        -------
        description : `str`
        """
        logger.debug("_Block.description called")
        return str(self._description)

    @description.setter
    def description(self, value):
        """
        A user-defined `str` description for the `~pyscope.telrun._Block`.

        Parameters
        ----------
        value : `str`

        """
        logger.debug("_Block.description(value=%s) called" % value)
        if type(value) is not str:
            logger.error(
                "The description parameter must be a string, not a %s", type(value)
            )
            logger.error("Ignoring the new description.")
            return
        logger.debug("Setting the description to %s" % value)
        self._description = value

    @property
    def kwargs(self):
        """
        Additional user-defined keyword arguments in a `dict` for the `~pyscope.telrun._Block`.

        Returns
        -------
        kwargs : `dict`

        """
        logger.debug("_Block.kwargs called")
        return dict(self._kwargs)

    @kwargs.setter
    def kwargs(self, value):
        """
        Additional user-defined keyword arguments for the `~pyscope.telrun._Block`.

        Parameters
        ----------
        value : `dict`

        """
        logger.debug("_Block.kwargs(value=%s) called" % value)
        if type(value) is not dict:
            logger.error("The kwargs parameter must be a dict, not a %s", type(value))
            logger.error("Ignoring the new keyword arguments.")
            return
        logger.debug("Setting the keyword arguments to %s" % value)
        self._kwargs = value

    @property
    def ID(self):
        """
        A `~uuid.UUID` that uniquely identifies the `~pyscope.telrun._Block`.

        Returns
        -------
        ID : `uuid.UUID`
            The unique identifier for the `~pyscope.telrun._Block`.
        """
        logger.debug("_Block.ID called")
        return uuid(self._uuid)

    @property
    def start_time(self):
        """
        The `~astropy.time.Time` that represents the start of the `~pyscope.telrun._Block`.

        Returns
        -------
        start_time : `astropy.time.Time`
            The start time of the `~pyscope.telrun._Block`.
        """
        logger.debug("_Block.start_time called")
        return Time(self._start_time)

    @property
    def end_time(self):
        """
        The `~astropy.time.Time` that represents the end of the `~pyscope.telrun._Block`.

        Returns
        -------
        end_time : `astropy.time.Time`
            The end time of the `~pyscope.telrun._Block`.
        """
        logger.debug("_Block.end_time called")
        return Time(self._end_time)
