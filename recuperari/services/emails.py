from django.core.mail import send_mail


class EmailService:
    @staticmethod
    def send_email(
        recipient_emails: list[str],
        message: str,
        subject: str,
        sender: str,
    ):
        subject = 'Hello, Shared Email!'
        message = 'This is a test email sent from my Django application using a shared email account.'
        from_email = sender
        recipient_list = recipient_emails

        send_mail(subject, message, from_email, recipient_list)
        print("Email sent successfully.")
