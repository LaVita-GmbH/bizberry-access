from django.conf import settings
from kombu import Connection


connection = Connection(
    settings.BROKER_URL,
    heartbeat=60,
)
