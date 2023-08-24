import datetime
import smtplib

gmail_user = "iota.alert@gmail.com"
gmail_password = "iowaTele1"

sent_from = gmail_user
to = ["chris@iapcrepair.com", "robert-mutel@uiowa.edu", "caroline-roberts@uiowa.edu"]
subject = "Gemini ECC PC Rebooted"
body = "Gemini ECC PC Rebooted at " + str(datetime.datetime.now())

email_text = """\
From: %s
To: %s
Subject: %s

%s
""" % (
    sent_from,
    ", ".join(to),
    subject,
    body,
)

try:
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.ehlo()
    server.login(gmail_user, gmail_password)
    server.sendmail(sent_from, to, email_text)
    server.close()

    print("Email sent!")
except:
    print("Something went wrong...")
