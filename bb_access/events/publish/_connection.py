from django.conf import settings
from kafka import KafkaProducer


connection = KafkaProducer(
    bootstrap_servers=settings.BROKER_URL,
    acks=settings.BROKER_ACKS,
    request_timeout_ms=settings.BROKER_REQUEST_TIMEOUT,
    security_protocol=settings.BROKER_SECURITY_PROTOCOL,
    sasl_mechanism=settings.BROKER_SASL_MECHANISM,
    sasl_plain_username=settings.BROKER_SASL_PLAIN_USERNAME,
    sasl_plain_password=settings.BROKER_SASL_PLAIN_PASSWORD,
    ssl_cafile=settings.BROKER_SSL_CERTFILE,
)
