import logging
import smtplib
from email.mime.text import MIMEText

def send_mail(gmail_username, gmail_password, recipients, subject, content):
    """
    Send an e-mail through Gmail's SMTP servers (using a valid
    Gmail account).

    gmail_username: the (username) portion of (username)@gmail.com
    gmail_password: the gmail password for the account
    recipients: either a string containing a single e-mail address
                or a list of [email1, email2, ...] addresses
    subject: the subject line of the message
    content: the body of the message
    """

    gmail_address = gmail_username

    if "@" not in gmail_address:
        gmail_address += "@gmail.com"


    logging.info("Sending email to %s", recipients)
    logging.info("Mail subject: %s", subject)
    logging.info("Mail content: %s", content)

    try:
        msg = MIMEText(content)
        msg['Subject'] = subject
        msg['From'] = gmail_username
        to_header = recipients
        if type(recipients) in (list, tuple):
            to_header = ", ".join(recipients)
        msg['To'] = to_header

        session = smtplib.SMTP('smtp.gmail.com', 587)
        #session.set_debuglevel(1)  # Uncomment to show extra diagnostics on the console
        session.ehlo()
        session.starttls()
        session.login(gmail_address, gmail_password)

        session.sendmail(gmail_address, recipients, msg.as_string())
    except Exception as ex:
        logging.error("Unable to send email: %s", ex)
        raise

    logging.info("Mail sent")

def runtests():
    from . import logutil
    logutil.setup_log()

    gmail_username = "iota.alert"
    gmail_password = input("Enter password for gmail user " + gmail_username + ": ")

    while True:
        test_type = input("Enter:\n"
            " 1 to send to all recipients at once, or \n"
            " 2 to send an individual email to each recipient")

        test_type = test_type.strip()
        if test_type in ['1', '2']:
            break

    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subject = "Alert sent at " + timestamp
    message = "This is a sample message sent from python"

    recipients = [
             "kivarsen@gmail.com", 
             "ivarnelispam@gmail.com", 
             "kivarsen@planewave.com", 
             "ivarneli@yahoo.com"
            ]

    if test_type == '1':
        send_mail(gmail_username, 
                gmail_password, 
                recipients,
                subject,
                message)
    else:
        for recipient in recipients:
            send_mail(gmail_username, 
                    gmail_password, 
                    recipient,
                    subject,
                    message)


if __name__ == "__main__":
    runtests()
