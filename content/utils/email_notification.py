import smtplib
from . import db_utils
from . import cfrenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_notification(composed_email):
    """
    Connects to NMSU's SMTP server to send an
    email notification.

    composed_email is a fully composed
    MIMEMultipart email message.
    """

    if not cfrenv.can_do_email():
        # If email isn't configured, forget it
        return

    host      = cfrenv.getenv('SMTP_SERVER')
    address     = cfrenv.getenv('SMTP_ADDRESS')
    password    = cfrenv.getenv('SMTP_PASSWORD')
    port        = cfrenv.getenv('SMTP_PORT')

    try:
        server = smtplib.SMTP(host=host, port=port)
        server.starttls()
        server.login(address, password)
        server.send_message(composed_email)
    except Exception:
        pass
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
    email_to_submitter['From'] = cfrenv.getenv('SMTP_ADDRESS')

    email_to_approvers['Subject'] = f'{dept} CFR Submission'
    email_to_approvers['To'] = ','.join(approver_emails)
    email_to_approvers['From'] = cfrenv.getenv('SMTP_ADDRESS')

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
    email_to_submitter['From'] = cfrenv.getenv('SMTP_ADDRESS')

    email_to_approvers['Subject'] = f'{dept} CFR Revision'
    email_to_approvers['To'] = ','.join(approver_emails)
    email_to_approvers['From'] = cfrenv.getenv('SMTP_ADDRESS')

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
    email_to_submitter['From'] = cfrenv.getenv('SMTP_ADDRESS')

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
    email_message['From'] = cfrenv.getenv('SMTP_ADDRESS')

    # Add message body
    message = f'Course funding request season for {season} is now open'
    email_message.attach(MIMEText(message, 'plain'))

    # Send email
    send_email_notification(email_message)
