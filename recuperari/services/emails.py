from django.core.mail import send_mail


class EmailService:
    @staticmethod
    def send_email(
        recipient_emails: list[str],
        message: str,
        subject: str,
        sender: str,
    ):
        print("SENDING MAIL")
        subject = subject
        message = message
        from_email = sender
        recipient_list = recipient_emails

        send_mail(subject, message, from_email, recipient_list)
        print("Email sent successfully.")
