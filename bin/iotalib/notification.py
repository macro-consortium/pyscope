import logging

from . import config_notification
from . import gmail

def send_info(subject_suffix, message):
    if not config_notification.valid_config:
        logging.error("Not sending e-mail notification: don't have a valid notification config")
        return

    subject = "INFO - " + subject_suffix

    send_mail(config_notification.values.info_emails, subject, message)

def send_error(subject_suffix, message):
    if not config_notification.valid_config:
        logging.error("Not sending e-mail notification: don't have a valid notification config")
        return

    subject = "ERROR - " + subject_suffix

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
