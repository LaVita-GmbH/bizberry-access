import json
from typing import List
from kombu import Exchange
from asgiref.sync import async_to_sync
from pydantic import BaseModel, Field
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from olympus.schemas import DataChangeEvent
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
    data = async_to_sync(response.User.from_orm)(instance).dict()

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
    connection.ensure(users, users.publish)(
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
    connection.ensure(users, users.publish)(
        message=body.json(),
        routing_key=f'v1.data.delete.{instance.tenant_id}',
    )
