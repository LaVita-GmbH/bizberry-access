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


class UserOTPPublisher(
    DataChangePublisher,
    EventPublisher,
    orm_model=models.UserOTP,
    event_schema=response.UserOTP,
    connection=connection,
    topic='bizberry.access.users.otps',
    data_type='access.user.otp',
    is_changed_included=True,
    is_post_delete_received=False,
):
    def get_body(self):
        return {
            'id': self.instance.id,
            'user': transfer_from_orm(response.User, self.instance.user).dict(by_alias=True),
            'value': self.instance._value,
            'expire_at': self.instance.expire_at.isoformat(),
        }

    def process(self):
        if not self.kwargs.get('created'):
            return

        if self.instance.is_internal:
            return

        return super().process()


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
