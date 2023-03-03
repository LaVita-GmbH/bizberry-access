import smtplib
import socket
from unidecode import unidecode
from email.message import EmailMessage
from email.headerregistry import Address
from django.conf import settings
from djutils.crypt import random_string_generator
from . import Sender


class EmailSender(Sender):
    MEDIUM = 'EMAIL'


class SMTPEmailSender(EmailSender):
    INTEGRATION = 'SMTP'

    def _get_message(self):
        message = EmailMessage()
        message['Subject'] = self.content.subject
        message['From'] = Address(settings.SENDER_EMAIL_INTEGRATION_SMTP_SENDER_NAME, addr_spec=settings.SENDER_EMAIL_INTEGRATION_SMTP_SENDER_EMAIL)
        message['To'] = self.content.receiver
        message['Message-ID'] = f'<{random_string_generator(size=64)}@{socket.getfqdn()}>'

        message.set_default_type('message/rfc822')
        message.add_alternative(self.content.body, subtype='html')

        return message

    def _send_message(self, message):
        connection = smtplib.SMTP
        if settings.SENDER_EMAIL_INTEGRATION_SMTP_USE_SSL and not settings.SENDER_EMAIL_INTEGRATION_SMTP_USE_STARTTLS:
            connection = smtplib.SMTP_SSL

        with connection(
            host=settings.SENDER_EMAIL_INTEGRATION_SMTP_HOST,
            port=settings.SENDER_EMAIL_INTEGRATION_SMTP_PORT,
            timeout=settings.SENDER_EMAIL_INTEGRATION_SMTP_TIMEOUT,
        ) as smtp:
            if settings.SENDER_EMAIL_INTEGRATION_SMTP_USE_STARTTLS:
                smtp.starttls()

            if settings.SENDER_EMAIL_INTEGRATION_SMTP_USER and settings.SENDER_EMAIL_INTEGRATION_SMTP_PASSWORD:
                smtp.login(
                    user=settings.SENDER_EMAIL_INTEGRATION_SMTP_USER,
                    password=settings.SENDER_EMAIL_INTEGRATION_SMTP_PASSWORD,
                )

            smtp.send_message(message)

    def send(self):
        while True:
            try:
                message = self._get_message()
                self._send_message(message)

            except smtplib.SMTPNotSupportedError as error:
                if isinstance(error.__cause__, UnicodeDecodeError):
                    self.content.receiver = unidecode(self.content.receiver.replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue'))

                else:
                    raise

            else:
                break
