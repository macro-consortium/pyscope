# Built-in Python imports
import logging
import threading
import time

# iotalib imports
from . import logutil
from . import notification
from . import config_notification

def start():
    """
    Called by the client to kick off the e-mail warning notification thread
    """

    logging.info("Starting warning e-mailer thread")

    thread = threading.Thread(target=_thread_loop)
    thread.daemon = True
    thread.start()

def _thread_loop():
    """
    Periodically accumulate any log messages of level WARNING or higher
    and e-mail them to interested parties
    """

    while True:
        try:
            if not logutil.warning_queue.empty():
                logging.info("Sending warning e-mails")
                notification.send_warnings()
        except Exception as ex:
            logging.exception("Error sending warning emails")
        
        time.sleep(config_notification.values.warning_email_min_interval_seconds)
