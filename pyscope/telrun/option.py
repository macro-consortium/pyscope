import logging

logger = logging.getLogger(__name__)


class Option:
    def __init__(
        self,
        name="",
        instruments=[],
        current_value=None,
        default_value=None,
        description="",
        type="str",  # str, int, float, bool, list, dict
        **kwargs
    ):
        """
        Add a new schedulable `~pyscope.telrun.Option` to the `~pyscope.telrun.InstrumentConfiguration`.

        The `~pyscope.telrun.Option` class is used to define an `~pyscope.telrun.Option` that a user can set in a `~pyscope.telrun.ScheduleBlock` by
        modifying the requested `~pyscope.telrun.InstrumentConfiguration`. This class is used to define the options that are available
        to the user and to validate the values that are set for the options using an `~pyscope.telrun.InstrumentConfiguration` that
        is contained in the `~pyscope.telrun.TelrunOperator`.

        Parameters
        ----------
        name : `str`, default : ""
            The name of the `~pyscope.telrun.Option`. This is used to identify the `~pyscope.telrun.Option` in the `~pyscope.telrun.InstrumentConfiguration` and
            must be unique within the configuration.

        instruments : `list` of `str`, default : []
            The list of instruments used by the `~pyscope.telrun.Option`. This can be used to sort options by instrument.

        current_value : `str`, `int`, `float`, `bool`, `list`, `dict`, default : `None`
            The current value of the `~pyscope.telrun.Option`. This is the value that will be used in the observation if the `~pyscope.telrun.Option` is not changed.

        default_value : `str`, `int`, `float`, `bool`, `list`, `dict`, default : `None`
            The default value of the `~pyscope.telrun.Option`. This is the value that will be used if the `~pyscope.telrun.Option` is not set by the user.

        description : `str`, default : ""
            A description of the `~pyscope.telrun.Option`. This is used to provide information to the user about the `~pyscope.telrun.Option`.

        type : `str`, default : "str"
            The type of the `~pyscope.telrun.Option`. This can be one of "str", "int", "float", "bool", "list", or "dict".

        **kwargs : `dict`, default : {}
            Additional keyword arguments to pass to the `~pyscope.telrun.Option`. If `type="list"` or `type="dict"`, requested values
            will be validated against `vlist` or `vdict` respectively. If `type="int"` or `type="float"`, the value will be validated
            against `min` and `max` if they are set. If `type="bool"`, the value will be converted to a `bool`. If `type="str"`, the
            value will be validated against a list of `str` values in `vlist` if it is set or the length of the string will be validated
            against `min` and `max` if they are set.

        """
        logger.debug(
            "Option(name=%s, instruments=%s, current_value=%s, default_value=%s, description=%s, type=%s, kwargs=%s)"
            % (
                name,
                instruments,
                current_value,
                default_value,
                description,
                type,
                kwargs,
            )
        )

    @classmethod
    def from_string(
        cls,
        string,
        name=None,
        instruments=None,
        current_value=None,
        default_value=None,
        description=None,
        type=None,
        **kwargs
    ):
        """
        Create a `~pyscope.telrun.Option` or a `list` of `~pyscope.telrun.Option` objects from a `str` representation of a `~pyscope.telrun.Option`.
        All optional parameters are used to override the parameters extracted from the `str` representation.

        Parameters
        ----------
        string : `str`, required

        name : `str`, default : `None`

        instruments : `list` of `str`, default : `None`

        current_value : `str`, `int`, `float`, `bool`, `list`, `dict`, default : `None`

        default_value : `str`, `int`, `float`, `bool`, `list`, `dict`, default : `None`

        description : `str`, default : `None`

        type : `str`, default : `None`

        **kwargs : `dict`, default : {}

        Returns
        -------
        `~pyscope.telrun.Option` or `list` of `~pyscope.telrun.Option`

        """
        logger.debug(
            "Option.from_string(string=%s, name=%s, instruments=%s, current_value=%s, default_value=%s, description=%s, type=%s, kwargs=%s)"
            % (
                string,
                name,
                instruments,
                current_value,
                default_value,
                description,
                type,
                kwargs,
            )
        )

    def __str__(self):
        """
        Return a `str` representation of the `~pyscope.telrun.Option`.

        Returns
        -------
        `str`
            A `str` representation of the `~pyscope.telrun.Option`.
        """
        logger.debug("Option().__str__() = %s" % self)

    def __repr__(self):
        """
        Return a `str` representation of the `~pyscope.telrun.Option`.

        Returns
        -------
        `str`
            A `str` representation of the `~pyscope.telrun.Option`.
        """
        logger.debug("Option().__repr__() = %s" % self)
        return str(self)

    def __call__(self):
        logger.debug("Option().__call__()")
