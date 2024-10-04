import logging

logger = logging.getLogger(__name__)


class Option:
    def __init__(
        self,
        name="",
        instruments=None,
        current_value=None,
        default_value=None,
        description="",
        type="str",  # str, int, float, bool, list, dict
        **kwargs
    ):
        pass
