import logging
import logging.handlers
import os
import queue

from . import paths

LOGFILE_FORMAT='%(asctime)s.%(msecs)03d %(message)s [%(filename)s:%(lineno)s - %(funcName)s() %(levelname)s]'
LOGFILE_DATEFORMAT='%Y-%m-%d %H:%M:%S'
LOGFILE_MAX_BYTES = 50000000
LOGFILE_BACKUP_COUNT = 20

CONSOLE_FORMAT='%(asctime)s.%(msecs)03d %(message)s'
CONSOLE_DATEFORMAT='%H:%M:%S'


def setup_log(log_filename=None):
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    console_formatter = logging.Formatter(fmt=CONSOLE_FORMAT, datefmt=CONSOLE_DATEFORMAT)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    gui_queue_formatter = logging.Formatter(fmt=CONSOLE_FORMAT, datefmt=CONSOLE_DATEFORMAT)
    gui_queue_handler = QueueHandler(log_message_queue, 1000)
    gui_queue_handler.setLevel(logging.DEBUG)
    gui_queue_handler.setFormatter(gui_queue_formatter)
    root_logger.addHandler(gui_queue_handler)

    warning_queue_formatter = logging.Formatter(fmt=CONSOLE_FORMAT, datefmt=LOGFILE_DATEFORMAT)
    warning_queue_handler = QueueHandler(warning_queue, 1000)
    warning_queue_handler.setLevel(logging.WARNING)
    warning_queue_handler.setFormatter(warning_queue_formatter)
    root_logger.addHandler(warning_queue_handler)

    recent_queue_formatter = logging.Formatter(fmt=CONSOLE_FORMAT, datefmt=LOGFILE_DATEFORMAT)
    recent_queue_handler = QueueHandler(recent_message_queue, 100)
    recent_queue_handler.setLevel(logging.DEBUG)
    recent_queue_handler.setFormatter(recent_queue_formatter)
    root_logger.addHandler(recent_queue_handler)

    if log_filename is not None:
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

# QueueHandler will accumulate all messages in this queue, which
# can be picked up from elsewhere (such as in the GUI)
log_message_queue = queue.Queue()

# Log messages of level Warning and higher get written to this
# queue to be periodically emailed out
warning_queue = queue.Queue()

# A small set of recent messages roll through this queue to be
# sent out with error e-mails to describe the events leading up
# to the error
recent_message_queue = queue.Queue()

class QueueHandler(logging.Handler):
    """
    A logging handler that writes messages to a FIFO queue.
    Messages can be periodically read from the queue; for example,
    in a Tkinter event handler
    """

    def __init__(self, queue, max_entries):
        """
        queue: a reference to an instance of Queue. Messages written to this
               handler will be added to the queue

        max_entries: the most entries stored in the queue before the oldest
                     items start getting thrown out
        """

        logging.Handler.__init__(self)
        self.queue = queue
        self.max_queue_size = max_entries

    def reduce_to_maxsize(self):
        while self.queue.qsize() >= self.max_queue_size:
            self.queue.get()

    def emit(self, message):
        """
        Overwrites the default handler's emit method
        """

        formatted_message = self.format(message)
        self.reduce_to_maxsize()
        self.queue.put(formatted_message)

