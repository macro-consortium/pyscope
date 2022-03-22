import logging
import logging.handlers
import os

from . import paths

LOGFILE_FORMAT='%(asctime)s.%(msecs)03d %(message)s [%(filename)s:%(lineno)s - %(funcName)s() %(levelname)s]'
LOGFILE_DATEFORMAT='%Y-%m-%d %H:%M:%S'
LOGFILE_MAX_BYTES = 50000000
LOGFILE_BACKUP_COUNT = 20

CONSOLE_FORMAT='%(asctime)s.%(msecs)03d %(message)s'
CONSOLE_DATEFORMAT='%H:%M:%S'


def setup_log(log_filename):
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    console_formatter = logging.Formatter(fmt=CONSOLE_FORMAT, datefmt=CONSOLE_DATEFORMAT)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    log_filepath = os.path.join(get_default_log_dir(), log_filename)
    logging.info("Logging to file %s", log_filepath)

    log_dir = os.path.dirname(log_filepath)
    if not os.path.isdir(log_dir):
        logging.info("Creating directory %s", log_dir)
        os.makedirs(log_dir)

    file_formatter = logging.Formatter(fmt=LOGFILE_FORMAT, datefmt=LOGFILE_DATEFORMAT)
    file_handler = logging.handlers.RotatingFileHandler(log_filepath, maxBytes=LOGFILE_MAX_BYTES, backupCount=LOGFILE_BACKUP_COUNT)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)


def get_default_log_dir():
    """
    By default, the "logs" directory lives under:
      IOTAHOME\logs
    and we live under:
      IOTAHOME\iota\iotalib\logutil.py
    So we need to find the directory "..\..\logs" relative to
    our current script location
    """

    return paths.log_dir()

def mkdir_p(path):
    """http://stackoverflow.com/a/600612/190597 (tzot)"""
    try:
        os.makedirs(path, exist_ok=True)  # Python>3.2
    except TypeError:
        try:
            os.makedirs(path)
        except OSError as exc: # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else: raise


