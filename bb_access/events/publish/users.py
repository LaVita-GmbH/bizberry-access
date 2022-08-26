from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from djdantic.utils.pydantic_django import transfer_from_orm
from djpykafka.events.publish import EventPublisher, DataChangePublisher
from ... import models
from ...schemas import response
from . import connection


class UserPublisher(
    DataChangePublisher,
    EventPublisher,
    orm_model=models.User,
    event_schema=response.User,
    connection=connection,
    topic='bizberry.access.users',
    data_type='access.user',
    is_changed_included=True,
):
    pass


class UserLoginPublisher(
    EventPublisher,
    orm_model=models.User,
    event_schema=response.User,
    connection=connection,
    topic='bizberry.access.users.login',
    data_type='access.user.login',
):
    @classmethod
    def register(cls):
        receiver(user_logged_in)(cls.handle)
