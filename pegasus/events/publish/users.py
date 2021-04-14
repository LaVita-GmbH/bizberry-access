from kombu import Exchange
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from olympus.schemas import DataChangeEvent
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


@receiver(post_save, sender=models.User)
def post_save_user(sender, instance: models.User, created: bool, **kwargs):
    action = 'create' if created else 'update'
    data = transfer_from_orm(response.User, instance).dict(by_alias=True)

    modified = instance.get_dirty_fields(check_relationship=True)
    data['_changed'] = [
        {
            'name': field,
        } for field, _value in modified.items()
    ]

    body = DataChangeEvent(
        data=data,
        data_type='access.user',
        data_op=getattr(DataChangeEvent.DataOperation, action.upper()),
        tenant_id=instance.tenant_id,
    )
    connection.ensure(users, users.publish, max_retries=3)(
        message=body.json(),
        routing_key=f'v1.data.{action}.{instance.tenant_id}',
    )


@receiver(post_delete, sender=models.User)
def post_delete_user(sender, instance: models.User, **kwargs):
    body = DataChangeEvent(
        data={
            'id': instance.id,
        },
        data_type='access.user',
        data_op=DataChangeEvent.DataOperation.DELETE,
        tenant_id=instance.tenant_id,
    )
    connection.ensure(users, users.publish, max_retries=3)(
        message=body.json(),
        routing_key=f'v1.data.delete.{instance.tenant_id}',
    )


@receiver(post_save, sender=models.UserOTP)
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

    connection.ensure(users, users.publish, max_retries=3)(
        message=body.json(),
        routing_key=f'v1.action.otp_{str(instance.type).lower()}.{instance.user.tenant_id}',
    )
