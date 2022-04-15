import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def send_email(to_email, subject, html_content):
    message = Mail(
        from_email="BISV.Book.Exchange.Club@gmail.com",
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )
    try:
        api_key = os.environ.get('SENDGRID_API_KEY')
        sg = SendGridAPIClient(api_key)
        sg.send(message)
        print('Sent Email To: ' + to_email)
    except Exception as e:
        print('send_email Exception: ' + str(e))
