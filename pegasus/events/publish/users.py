import json
from kombu import Exchange
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from ... import models
from ...schemas import response
from ..base import connection


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
    body = async_to_sync(response.User.from_orm)(instance, tenant=None).json()
    connection.ensure(users, users.publish)(
        message=body,
        routing_key=f'v1.data.{action}',
    )


@receiver(post_delete, sender=models.User)
def post_delete_user(sender, instance: models.User, **kwargs):
    body = json.dumps({'id': instance.id})
    connection.ensure(users, users.publish)(
        message=body,
        routing_key='v1.data.delete',
    )
