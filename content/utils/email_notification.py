import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# SET AS ENVIRONMENT VARIABLES:
SENDER_ADDRESS = 'CFR@nmsu.edu'
PASSWORD = 'newmexicostate2019'

def send_email_notification(composed_email):
    """
    Connects to NMSU's SMTP server to send an
    email notification.

    composed_email is a fully composed
    MIMEMultipart email message.
    """

    try:
        server = smtplib.SMTP(host='smtp.nmsu.edu', port=587)
        server.starttls()
        server.login(SENDER_ADDRESS, PASSWORD)
        server.send_message(composed_email)
    except Exception as e:
        print(e)
    finally:
        server.quit()

def compose_new_cfr_email(dept, submitter_emails, approver_emails):
    """
    Composes a an email notification to be sent when a new
    CFR is created.

    dept is the name of the department the submission is for
    submitter_email is the email of the submitting party
    approver_emails is a list of all approver's emails
    """

    # create message
    email_to_submitter = MIMEMultipart()
    email_to_approvers = MIMEMultipart()

    # set up message parameters
    email_to_submitter['Subject'] = f'{dept} CFR Submission'
    email_to_submitter['To'] = ','.join(submitter_emails)
    email_to_submitter['From'] = SENDER_ADDRESS

    email_to_approvers['Subject'] = f'{dept} CFR Submission'
    email_to_approvers['To'] = ','.join(approver_emails)
    email_to_approvers['From'] = SENDER_ADDRESS

    # add message body
    message_to_submitter = f'Your Course Funding Request for {dept} has been submitted.'
    email_to_submitter.attach(MIMEText(message_to_submitter, 'plain'))

    message_to_approvers = f'A Course Funding Request for {dept} has been submitted.'
    email_to_approvers.attach(MIMEText(message_to_approvers, 'plain'))

    # send message
    send_email_notification(email_to_submitter)
    send_email_notification(email_to_approvers)

def compose_cfr_revision_email(dept, submitter_email, approver_emails):
    """
    Composes a an email notification to be sent when a
    revision is made to an existing CFR.

    dept is the name of the department the submission is for
    submitter_email is the email of the submitting party
    approver_emails is a list of all approver's emails
    """

    # create message
    email_to_submitter = MIMEMultipart()
    email_to_approvers = MIMEMultipart()

    # set up message parameters
    email_to_submitter['Subject'] = f'{dept} CFR Revision'
    email_to_submitter['To'] = f'{submitter_email}'
    email_to_submitter['From'] = SENDER_ADDRESS

    email_to_approvers['Subject'] = f'{dept} CFR Revision'
    email_to_approvers['To'] = ','.join(approver_emails)
    email_to_approvers['From'] = SENDER_ADDRESS

    # add message body
    message_to_submitter = f'Your revision has been submitted for {dept}.'
    email_to_submitter.attach(MIMEText(message_to_submitter, 'plain'))

    message_to_approvers = f'A revision has been made to {dept}\'s Course Funding Request.'
    email_to_approvers.attach(MIMEText(message_to_approvers, 'plain'))

    # send message
    send_email_notification(email_to_submitter)
    send_email_notification(email_to_approvers)

def compose_cfr_status_email(dept, submitter_email):
    """
    Composes a an email notification to be sent when the
    status of a CFR changes dues to approvals/denials.

    dept is the name of the department the submission is for
    submitter_email is the email of the department head whose
    CFR status was updated
    """

    # create message
    email_to_submitter = MIMEMultipart()

    # set up message parameters
    email_to_submitter['Subject'] = f'{dept} CFR Status Update'
    email_to_submitter['To'] = f'{submitter_email}'
    email_to_submitter['From'] = SENDER_ADDRESS

    # add message body
    message_to_submitter = f'The status of {dept}\'s Course Funding Request has been determined.'
    email_to_submitter.attach(MIMEText(message_to_submitter, 'plain'))

    # send message
    send_email_notification(email_to_submitter)