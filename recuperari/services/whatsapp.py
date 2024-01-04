import requests
from recuperari.models import SentWhatsappMessages


class WhatsappService:
    @staticmethod
    def send_whatsapp_message(recipient, message):
        phone_number_id = "179362605250434"
        token = "EAAKHLG1mIXwBOwAExEruZBGj0NKZAgyx60ZAFDJej88WZB6OTjHvgGz3lnZASUia7ZBGACMBHofkewZByH4ZCemjuzJylZA25ze2NHuRCx3ygcCOTPQKoRzCutZAwbxMMOu2hOf3Ue7zwPd3zpn8atO4S0g9ZCRVFOOfTsVPeNBHnDTCTo8VlNxMfb0XpDbIXKGh9afMMImmPpfZAMmCCe5GdqNUqqhKpffiZBAFZAg3Wv"
        error_message = None
        has_errors = False

        url = f'https://graph.facebook.com/v18.0/{phone_number_id}/messages'

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }

        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "preview_url": False,
            "to": recipient,
            "type": "template",
            "template": {
                "name": "mesaj_initial_plus_notificare_curs",
                "language": {"code": "ro"}
            }
        }

        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            has_errors = True
            error_message = response.text

        SentWhatsappMessages.objects.create(
            sent_to_number=recipient,
            sent_message=message,
            has_errors=has_errors,
            error_message=error_message,
        )
