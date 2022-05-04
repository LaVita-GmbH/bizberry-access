from ensurepip import bootstrap
from django.conf import settings
from kafka import KafkaProducer


connection = KafkaProducer(
    bootstrap_servers=settings.BROKER_URL,
)
