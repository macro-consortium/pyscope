"""
Function for reading, parsing, and validating config files
"""

import configparser, os

def read(config_file):

    try:
        config = configparser.RawConfigParser()   
        config.read(config_file)
    except Exception as ex:
        raise Exception("Error parsing config file '%s'" % config_file, ex)

    return config