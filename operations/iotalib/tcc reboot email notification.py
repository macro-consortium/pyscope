from gmail import *


#send_mail(gmail_username, gmail_password, recipients, subject, content)


# Send alert e-mails from this Gmail account
gmail_username = "iota.alert"
gmail_password = "iowaTele1"

# Send fatal errors (crashes) to these addresses
error_emails = [
    "kivarsen@gmail.com",
    "robert-mutel@uiowa.edu",
    "christopher-michael@uiowa.edu",
	"caroline-roberts@uiowa.edu",
	"joshua-kamp@uiowa.edu"
]

subject = "TCC reboot"
content = "This email is to notify you that the TCC has been restarted or has crashed and rebooted."

send_mail(gmail_username, gmail_password, error_emails, subject, content)
#send_mail(gmail_username, gmail_password, ["jua.kamp451@gmail.com"], subject, content)