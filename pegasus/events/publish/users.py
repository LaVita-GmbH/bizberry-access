from kombu import Exchange
from django.db.models.signals import post_save
from django.dispatch import receiver
from olympus.schemas import DataChangeEvent
from olympus.events.publish import EventPublisher, DataChangePublisher
from olympus.utils.django import on_transaction_complete
from django.contrib.auth.signals import user_logged_in
from olympus.utils.pydantic_django import transfer_from_orm
from ... import models
from ...schemas import response
from . import connection


users = Exchange(
    name='olymp.access.users',
    type='topic',
    durable=True,
    channel=connection.channel(),
    delivery_mode=Exchange.PERSISTENT_DELIVERY_MODE,
)
users.declare()
producer = connection.Producer(exchange=users)


class UserPublisher(
    DataChangePublisher,
    EventPublisher,
    orm_model=models.User,
    event_schema=response.User,
    connection=connection,
    exchange=users,
    data_type='access.user',
    is_changed_included=True,
):
    pass


@receiver(post_save, sender=models.UserOTP)
@on_transaction_complete()
def post_save_user_otp(sender, instance: models.UserOTP, created: bool, **kwargs):
    if not created:
        return

    if instance.is_internal:
        return

    body = DataChangeEvent(
        data={
            'id': instance.id,
            'user': {
                'id': instance.user_id,
                '$rel': 'olymp/access/users',
            },
            'value': instance._value,
            'expire_at': instance.expire_at.isoformat(),
        },
        data_type='access.user.otp',
        data_op=DataChangeEvent.DataOperation.CREATE,
        tenant_id=instance.user.tenant_id,
    )

    producer.publish(
        retry=True,
        retry_policy={'max_retries': 3},
        body=body.json(),
        content_type='application/json',
        routing_key=f'v1.action.otp_{str(instance.type).lower()}.{instance.user.tenant_id}',
    )


@receiver(user_logged_in)
def on_user_logged_in(sender, instance: models.User, **kwargs):
    data = transfer_from_orm(response.User, instance).dict(by_alias=True)
    body = DataChangeEvent(
        data={
            'id': instance.id,
            'user': data,
        },
        data_type='access.user.login',
        data_op=DataChangeEvent.DataOperation.CREATE,
        tenant_id=instance.tenant_id,
    )

    producer.publish(
        retry=True,
        retry_policy={'max_retries': 3},
        body=body.json(),
        content_type='application/json',
        routing_key=f'v1.action.login.{instance.tenant_id}',
    )
