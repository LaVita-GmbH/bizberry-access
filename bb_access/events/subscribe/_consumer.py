from djpykafka.handlers.event_consumer import Consumer


consumer = Consumer(
    group_id="bizberry.access",
)
