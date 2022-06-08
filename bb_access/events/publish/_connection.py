from django.conf import settings
from kafka import KafkaProducer


connection = KafkaProducer(
    bootstrap_servers=settings.BROKER_URL,
    acks=settings.BROKER_ACKS,
    request_timeout_ms=settings.BROKER_REQUEST_TIMEOUT,
)
