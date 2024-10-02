import logging

from astropy.time import Time

from ._block import _Block

logger = logging.getLogger(__name__)


class UnallocatedBlock(_Block):
    def __init__(
        self,
        start_time,
        end_time,
        *args,
        config=None,
        name=None,
        description=None,
        **kwargs
    ):
        """
        A block of time that is not allocated to any fields.

        Parameters
        ----------
        start_time : `~astropy.time.Time`, required
            The start time of the `~pyscope.telrun.UnallocatedBlock`.

        end_time : `~astropy.time.Time`, required
            The end time of the `~pyscope.telrun.UnallocatedBlock`.

        *args : `tuple`
            If provided, the next argument should be a string representation of a `~pyscope.telrun.UnallocatedBlock`. The `from_string`
            class method will parse the string representation and create a new `~pyscope.telrun.UnallocatedBlock` object. The remaining
            arguments will override the parsed values.

        config : `~pyscope.telrun.Configuration`, default: `None`
            The `~pyscope.telrun.Configuration` to use for the `~pyscope.telrun.UnallocatedBlock`. This `~pyscope.telrun.Configuration` will be
            used to set the telescope's `~pyscope.telrun.Configuration` at the start of the `~pyscope.telrun.UnallocatedBlock`.

        name : `str`, default: `None`
            A user-defined name for the `~pyscope.telrun.UnallocatedBlock`. This parameter does not change
            the behavior of the `~pyscope.telrun.UnallocatedBlock`, but it can be useful for identifying the
            `~pyscope.telrun.UnallocatedBlock` in a schedule.

        description : `str`, default: `None`
            A user-defined description for the `~pyscope.telrun.UnallocatedBlock`. Similar to the `name`
            parameter, this parameter does not change the behavior of the `~pyscope.telrun.UnallocatedBlock`.

        **kwargs : `dict`
            A dictionary of keyword arguments that can be used to store additional information
            about the `~pyscope.telrun.UnallocatedBlock`. This information can be used to store any additional
            information that is not covered by the `configuration`, `name`, or `description` parameters

        """

        if len(args) == 3 and isinstance(args[2], str):
            self = self.from_string(
                args[2], config=config, name=name, description=description, **kwargs
            )
            self.start_time = args[0]
            self.end_time = args[1]
        elif len(args) == 1 and isinstance(args[0], str):
            self = self.from_string(
                args[0], config=config, name=name, description=description, **kwargs
            )
        elif len(args) != 2:
            raise ValueError("UnallocatedBlock requires 2 arguments.")
        else:
            self.start_time = start_time
            self.end_time = end_time

        super().__init__(
            *args, config=config, name=name, description=description, **kwargs
        )

    @classmethod
    def from_string(cls, *args, config=None, name=None, description=None, **kwargs):
        """
        Create a new `~pyscope.telrun.UnallocatedBlock` object from a string representation.

        Parameters
        ----------
        string : `str`, required
            The string representation of the `~pyscope.telrun.UnallocatedBlock`.

        Returns
        -------
        `~pyscope.telrun.UnallocatedBlock`
            A new `~pyscope.telrun.UnallocatedBlock` object created from the string representation.
        """
        logger.debug("UnallocatedBlock.from_string()")

        if len(args) == 1:
            string = args[0]
            start_time = None
            end_time = None
        elif len(args) == 3:
            string = args[2]
            start_time = args[0]
            end_time = args[1]
        else:
            raise ValueError("UnallocatedBlock.from_string requires 1 or 3 arguments.")

        n_blocks = string.count(
            "******************** Start UnallocatedBlock ********************"
        )
        end_blocks = string.count(
            "******************** End UnallocatedBlock ********************"
        )
        if n_blocks != end_blocks:
            raise ValueError("UnallocatedBlock string representation is malformed.")
        logger.debug("n_blocks=%i" % n_blocks)
        blocks = []
        for i in range(n_blocks):
            logger.debug("i=%i" % i)
            block_info = string.split(
                "******************** Start UnallocatedBlock ********************"
            )[i + 1].split(
                "******************** End UnallocatedBlock ********************"
            )[
                0
            ]
            logger.debug("block_info=%s" % block_info)

            block = super().from_string(
                block_info, config=config, name=name, description=description, **kwargs
            )
            block._start_time = (
                Time(start_time) if start_time is not None else block._start_time
            )
            block._end_time = (
                Time(end_time) if end_time is not None else block._end_time
            )
            logger.debug("block=%s" % block)

            blocks.append(block)

        if len(blocks) == 1:
            return blocks[0]
        return blocks

    def __str__(self):
        """
        Return a string representation of the `~pyscope.telrun.UnallocatedBlock`.

        Returns
        -------
        `str`
            A string representation of the `~pyscope.telrun.UnallocatedBlock`.
        """
        logger.debug("UnallocatedBlock.__str__()")
        s = "\n******************** Start UnallocatedBlock ********************\n"
        s += super().__str__()
        s += "\n******************** End UnallocatedBlock ********************"
        return s

    @start_time.setter
    def start_time(self, value):
        """
        The start time of the `~pyscope.telrun.UnallocatedBlock`.

        Parameters
        ----------
        value : `~astropy.time.Time`, required
            The start time of the `~pyscope.telrun.UnallocatedBlock`.
        """

        self._start_time = Time(value)

    @end_time.setter
    def end_time(self, value):
        """
        The end time of the `~pyscope.telrun.UnallocatedBlock`.

        Parameters
        ----------
        value : `~astropy.time.Time`, required
            The end time of the `~pyscope.telrun.UnallocatedBlock`.
        """

        self._end_time = Time(value)
