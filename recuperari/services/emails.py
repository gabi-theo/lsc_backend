from django.core.mail import send_mail
from django.template.loader import render_to_string


class EmailService:
    @staticmethod
    def send_email(
        recipient_emails,
        message: str,
        subject: str,
        sender: str,
    ):
        subject = subject
        message = message
        from_email = sender
        recipient_list = list(set(recipient_emails))
        for recipient in recipient_list:
            if(len(recipient.split(",")) >= 2):
                recipient = recipient.split(",")
            else:
                recipient = [recipient]
            try:
                send_mail(
                    subject,
                    render_to_string('emails/vacanta.txt'),
                    from_email,
                    recipient,
                )
                print(f"Mail sent to: {recipient}")
            except Exception as e:
                print(f"Error sending email to: {recipient}. Original error caused by: {e}")
