# Built-in Python imports
import logging
import queue

# iotalib imports
from . import config_notification
from . import gmail
from . import logutil

def send_info(subject_suffix, message):
    if not config_notification.valid_config:
        logging.error("Not sending e-mail notification: don't have a valid notification config")
        return

    subject = "INFO - " + subject_suffix

    send_mail(config_notification.values.info_emails, subject, message)

def send_warnings():
    if not config_notification.valid_config:
        logging.error("Not sending e-mail notification: don't have a valid notification config")
        return

    warnings = []
    while True:
        try:
            warning_message = logutil.warning_queue.get_nowait()
            warnings.append(warning_message)
        except queue.Empty:
            break

    subject = "%d Recent IOTA Warnings" % len(warnings)
    message = "\n".join(warnings)

    send_mail(config_notification.values.error_emails, subject, message)


def send_error(subject_suffix, message):
    if not config_notification.valid_config:
        logging.error("Not sending e-mail notification: don't have a valid notification config")
        return

    subject = "ERROR - " + subject_suffix

    try:
        log_messages = []
        while True:
            try:
                log_message = logutil.recent_message_queue.get_nowait()
                log_messages.append(log_message)
            except queue.Empty:
                break
        log_messages_text = "%d most recent log messages:\n%s" % (
            len(log_messages),
            "\n".join(log_messages)
            )

        message = message + "\n\n" + log_messages_text
    except:
        pass # Don't let a problem with our log message retrieval prevent us from getting the message out

    send_mail(config_notification.values.error_emails, subject, message)


def send_mail(email_addresses, subject, message):
    if config_notification.values.simulate_email:
        logging.info("SIMULATED EMAIL: Recipients = '%r', Subject = '%s', Message = '%s'",
                email_addresses, subject, message)
    else:
        gmail.send_mail(
                config_notification.values.gmail_username, 
                config_notification.values.gmail_password, 
                email_addresses,
                subject, 
                message)
