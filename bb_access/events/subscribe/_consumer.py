from djpykafka.handlers.event_consumer import Consumer
from django.conf import settings


consumer = Consumer(
    bootstrap_servers=settings.BROKER_URL,
    group_id='bizberry.access',
    request_timeout_ms=settings.BROKER_REQUEST_TIMEOUT,
    session_timeout_ms=settings.BROKER_SESSION_TIMEOUT,
    security_protocol=settings.BROKER_SECURITY_PROTOCOL,
    sasl_mechanism=settings.BROKER_SASL_MECHANISM,
    sasl_plain_username=settings.BROKER_SASL_PLAIN_USERNAME,
    sasl_plain_password=settings.BROKER_SASL_PLAIN_PASSWORD,
    ssl_cafile=settings.BROKER_SSL_CERTFILE,
    max_poll_records=settings.BROKER_MAX_POLL_RECORDS,
    max_poll_interval_ms=settings.BROKER_MAX_POLL_INTERVAL_MS,
)
