import logging
import requests
from django.conf import settings
from .. import models
from . import Sender


_logger = logging.getLogger(__name__)


class SMSSender(Sender):
    MEDIUM = 'SMS'


class MailJetSMSSender(SMSSender):
    INTEGRATION = 'MAILJET'

    def send(self):
        to = self.content.get_receiver() or self.message.contact.phone_mobile
        if not to:
            raise ValueError('missing_phone_mobile')

        response = requests.post('https://api.mailjet.com/v4/sms-send', json={
            'Text': self.content.get_content(),
            'To': to.replace(' ', ''),
            'From': settings.SENDER_SMS_INTEGRATION_MAILJET_SENDER_NAME,
        }, headers={
            'Authorization': 'Bearer %s' % settings.SENDER_SMS_INTEGRATION_MAILJET_TOKEN,
        })
        _logger.debug("Sent SMS using MailJet: %s: %r", response, response.json())

        if not response.ok:
            _logger.error("Failed to send SMS using Mailjet: %s: %r", response, response.json())
            raise ValueError('sms_send_failed')
