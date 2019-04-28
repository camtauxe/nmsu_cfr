import smtplib
from . import db_utils
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# SET AS ENVIRONMENT VARIABLES:
SENDER_ADDRESS = 'CFR@nmsu.edu'
# not the real password
PASSWORD = 'password place holder'

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

def compose_new_cfr_email(dept):
    """
    Composes a an email notification to be sent when a new
    CFR is created.

    dept is the name of the department the submission is for.
    """
    # Get a list of submitter emails for a department
    submitter_emails = db_utils.get_emails_by_dept(dept)

    # Get a list of approver emails
    approver_emails = db_utils.get_emails_by_type('approver')

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

def compose_cfr_revision_email(dept):
    """
    Composes a an email notification to be sent when a
    revision is made to an existing CFR.

    dept is the name of the department the submission is for
    """
    # Get a list of submitter emails for a department
    submitter_emails = db_utils.get_emails_by_dept(dept)

    # Get a list of approver emails
    approver_emails = db_utils.get_emails_by_type('approver')

    # create message
    email_to_submitter = MIMEMultipart()
    email_to_approvers = MIMEMultipart()

    # set up message parameters
    email_to_submitter['Subject'] = f'{dept} CFR Revision'
    email_to_submitter['To'] = ','.join(submitter_emails)
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

def compose_cfr_status_email(dept):
    """
    Composes a an email notification to be sent when the
    status of a CFR changes dues to approvals/denials.

    dept is the name of the department the submission is for
    """
    # Get a list of submitter emails for a department
    submitter_emails = db_utils.get_emails_by_dept(dept)

    # create message
    email_to_submitter = MIMEMultipart()

    # set up message parameters
    email_to_submitter['Subject'] = f'{dept} CFR Status Update'
    email_to_submitter['To'] = ','.join(submitter_emails)
    email_to_submitter['From'] = SENDER_ADDRESS

    # add message body
    message_to_submitter = f'The status of {dept}\'s Course Funding Request has been determined.'
    email_to_submitter.attach(MIMEText(message_to_submitter, 'plain'))

    # send message
    send_email_notification(email_to_submitter)

def compose_open_semester_email(season):
    """
    Composes an email notification to be sent to all users
    when a cfr semester has been opened

    season is a string containing the name of the opened 
    semester: 'Fall', 'Spring', 'Summer'
    """
    # Get the email adresses of all users
    email_adresses = db_utils.get_all_emails()

    # Create message
    email_message = MIMEMultipart()

    # Set up parameters
    email_message['Subject'] = 'CFR season now open'
    email_message['TO'] = ','.join(email_adresses)
    email_message['From'] = SENDER_ADDRESS

    # Add message body
    message = f'Course funding request season for {season} is now open'
    email_message.attach(MIMEText(message, 'plain'))

    # Send email
    send_email_notification(email_message)
