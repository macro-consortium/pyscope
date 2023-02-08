"""
Functions for reading, parsing, and validating config files
"""

# Built-in Python imports
import logging
import os
import socket

# iotalib imports
from . import paths

def initialize():
    """
    Called when the module is imported to set the default 
    location for config files
    """

    global _config_home_path
    _config_home_path = paths.config_path()

    global _local_config_path
    _local_config_path = os.path.join(_config_home_path, socket.gethostname())

def read(file_path):
    """
    Locate a config file given by file_path, parse it as a python file, 
    and return a Configuration object containing any variables that were 
    introduced in the file.

    If file_path is an absolute path (e.g. C:\\some\\dir\\file.cfg), the 
    config file is loaded directly from that location. If it is a relative
    path, the path will be relative to the location configured by 
    set_config_home(), which is under IOTAHOME\config by default.
    """

    _globals = dict()
    _locals = Configuration(file_path)

    resolved_file_path = get_config_path(file_path)
    logging.info("Loading config '%s'" % resolved_file_path)

    try:
        file_contents = open(resolved_file_path).read()
        exec(file_contents, _globals, _locals)
    except Exception as ex:
        raise Exception("Error parsing config file '%s'" % resolved_file_path, ex)

    machine_file_path = get_machine_specific_config_path(resolved_file_path)
    if os.path.isfile(machine_file_path):
        logging.info("Overriding values with machine-specific config '%s'" % resolved_file_path)

        try:
            file_contents = open(machine_file_path).read()
            exec(file_contents, _globals, _locals)
        except Exception as ex:
            raise Exception("Error parsing config file '%s'" % resolved_file_path, ex)

    return _locals

def set_config_home(config_path):
    """
    Override the default location for config files
    """
    _config_home_path = config_path

def get_config_path(config_filename=None):
    """
    Return the absolute path to a config file, given either an absolute
    or relative filename specification. For example,
    get_config_path("c:\\foo\\bar\\baz.cfg") will simply return
        "c:\\foo\\bar\\baz.cfg"
    since it is an absolute path, while:
    get_config_path("baz.cfg")
    might return something like:
        "c:\\scripts\\IowaAutomation\\config\\baz.cfg"
    if the iota folder is contained within "c:\\scripts\\IowaAutomation"
    """
    if config_filename is None:
        return _config_home_path
    elif os.path.isabs(config_filename):
        return config_filename
    else:
        return os.path.abspath(os.path.join(_config_home_path, config_filename))

def get_machine_specific_config_path(config_filepath):
    """
    Given the path to a global config file, return the path
    to a machine-specific config file. Note that the file may
    not actually exist.
    """

    machine_name = socket.gethostname()

    (path, filename) = os.path.split(config_filepath)
    path = os.path.join(path, machine_name)
    return os.path.join(path, filename)

class Configuration(dict):
    """
    Contains values loaded form a config file.

    Acts like a standard Python dictionary, but also allows attribute
    access. For example:

    person = {}
    person["firstname"] = "George"
    person["lastname"] = "Washington"

    print person["lastname"] # Access the 'lastname' property
    print person.lastname    # Same result as above; slightly nicer syntax

    Also includes some methods for validating the expected entries
    in the config.
    """

    def __init__(self, config_filename):
        self._config_filename = config_filename

    def __getattr__(self, name):
        "Allow 'dot' access for reading dictionary values; e.g. print config.value"
        return self[name]

    def __setattr__(self, name, value):
        "Allow 'dot' access for writing dictionary values; e.g. config.value = 5"
        self[name] = value

    def raise_validation_error(self, name, value, message):
        """
        Raise an exception indicating that there was a problem
        validating the config file
        """

        raise Exception("Error in config file '%s', entry '%s', value %r: '%s'" % (
            self._config_filename,
            name,
            value,
            message))

    def require(self, name, datatype=None):
        """
        Verify that a config entry with the given name exists in the
        current configuration. 
        
        datatype: optional argument specifying the valid datatype (or
          tuple of valid datatypes) for the config entry.

        Returns the value if it exists and passes validation.
        Raises an exception if there is a validation error.
        """

        value = self.get(name)
        if value is None:
            raise Exception("Error in config file '%s': missing entry '%s'" % (
                self._config_filename,
                name))

        try:
            validate_datatype(value, datatype)
        except ValidationError as ex:
            self.raise_validation_error(name, value, ex.message)

        return value

    def require_and_convert(self, name, conversion_func):
        value = self.require(name)

        try:
            value = conversion_func(value)
        except Exception as ex:
            self.raise_validation_error(name, value, ex.message)

        self[value] = value
        return value


    def require_bool(self, name):
        """
        Verify that the Configuration contains a boolean value
        (True or False) with the given name.

        Raises an exception if there is a validation error
        """

        value = self.require(name, bool)
        self[name] = value
        return value

    def require_string(self, name):
        """
        Verify that the Configuration contains a string-like
        value with the given name.

        Raises an exception if there is a validation error
        """

        value = self.require(name, (str, str))
        self[name] = value
        return value

    def require_int(self, name, min_value=None, max_value=None):
        """
        Verify that the Configuration contains an an entry with the
        given name, and that the entry can be converted to a valid
        integer (optionally between min_value and max_value).

        Converts the config value to an int, or raises an exception
        if there is a validation error
        """

        value = self.require(name)

        try:
            value = validate_int(value, min_value, max_value)
        except ValidationError as ex:
            self.raise_validation_error(name, value, ex.message)

        self[name] = value
        return value

    def require_float(self, name, min_value=None, max_value=None):
        """
        Verify that the Configuration contains an an entry with the
        given name, and that the entry can be converted to a valid
        floating point number (optionally between min_value and max_value).

        Converts the config file to a float, or raises an exception
        if there is a validation error
        """

        value = self.require(name)

        try:
            value = validate_float(value, min_value, max_value)
        except ValidationError as ex:
            self.raise_validation_error(name, value, ex.message)

        self[name] = value
        return value

    def require_list(self, name, item_validation_type=None, item_validation_func=None):
        """
        Verify that the Configuration contains an an entry with the
        given name, and that the entry is a list or a tuple.

        name: The string name of the configuration entry

        item_validation_type: optional; a Python type (e.g. int, float, str) 
          to validate that each item in the list is of the correct type

        item_validation_func: optional; a function taking one argument which
          validates/converts the argument and returns the validated/converted
          value. If validation fails, should raise an exception with a 
          message describing the validation error.

        Examples:
          # Validate that the configuration contains a list_of_ints entry
          # which is a list containing only int values
          cfg.require_list("list_of_ints", int)  

          # Validate that the configuration contains a list_of_positives entry
          # which is a list containing only positive values
          cfg.require_list("list_of_positives", None, lambda x: validate_int(x, 0))  
        """

        value = self.require(name)

        if type(value) not in (list, tuple):
            self.raise_validation_error(name, value, "not a valid list")

        for i in range(len(value)):
            item = value[i]

            if item_validation_type is not None:
                try:
                    validate_datatype(item, item_validation_type)
                except ValidationError as ex:
                    self.raise_validation_error(name, value, 
                        "item %r is of type %s, but must be of type %s" % (
                        item, 
                        type(item), 
                        item_validation_type))

            if item_validation_func is not None:
                try:
                    value[i] = item_validation_func(item)
                except Exception as ex:
                    self.raise_validation_error(name, value, "item '%s' in list failed validation: %s" % (item, ex.message))

        self[name] = value
        return value


# Validation functions that can be used by require_* methods above or by
# general user code

def validate_datatype(value, datatype):
    if datatype is None:
        pass
    elif isinstance(datatype, type):
        if type(value) != datatype:
            raise ValidationError("value is of type '%s', but expected type '%s'" % (
                type(value), 
                datatype)
                )
    elif isinstance(datatype, tuple): 
        if type(value) not in datatype:
            raise ValidationError("value is of type '%s', but expected one of the types: '%s'" % (
                type(value), 
                datatype)
                )
    else:
        raise Exception("Usage error: datatype argument must be a type or a tuple of types")

    return value

def validate_int(value, min_value=None, max_value=None):
    # Allow string-like values containing representations of integers
    # (and integers themselves) to be converted to integers. 
    # Explicitly do NOT allow floats to be converted to integers. 
    # (num_retries = 3.14 would not make sense)
    validate_datatype(value, (int, str, str))

    try:
        value = int(value)
    except Exception as ex:
        raise ValidationError("value '%s' cannot be converted to an integer" % value)

    if min_value is not None and value < min_value:
        raise ValidationError("value '%s' is less than minimum '%s'" % (value, min_value))

    if max_value is not None and value > max_value:
        raise ValidationError("value '%s' is greater than maximum '%s'" % (value, max_value))

    return value


def validate_float(value, min_value, max_value):
    try:
        value = float(value)
    except Exception as ex:
        raise ValidationError("value '%s' cannot be converted to a floating point number" % value)

    if min_value is not None and value < min_value:
        raise ValidationError("value '%s' is less than minimum '%s'" % (value, min_value))

    if max_value is not None and value > max_value:
        raise ValidationError("value '%s' is greater than maximum '%s'" % (value, max_value))

    return value

class ValidationError(Exception):
    "Custom exception specific to validation errors"
    pass

# Set default path on module import
initialize()
