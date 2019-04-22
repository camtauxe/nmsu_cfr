import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SENDER_ADDRESS = 'CFR@nmsu.edu'
PASSWORD = 'newmexicostate2019' #prompt user to enter?

def send_email_notification():
    """
    Send email notification
    """

    # create message
    email = MIMEMultipart()

    # set up message parameters
    email['Subject'] = 'Test'
    email['To'] = 'nmsucfrjoe@mailinator.com'
    email['From'] = SENDER_ADDRESS

    # add message body
    message = 'This is the plain text message body'
    email.attach(MIMEText(message, 'plain'))

    # set up SMTP server
    try:
        server = smtplib.SMTP(host='smtp.nmsu.edu', port=587)
        server.starttls()
        server.login(SENDER_ADDRESS, PASSWORD)
        server.send_message(email)
    except Exception as e:
        print(e)    # print error message to stdout
    finally:
        server.quit()