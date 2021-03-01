import json
from kombu import Exchange
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from olympus.schemas import DataChangeEvent
from ... import models
from ...schemas import response
from . import connection


tenants = Exchange(
    name='olymp.access.tenants',
    type='topic',
    durable=True,
    channel=connection.channel(),
    delivery_mode=Exchange.PERSISTENT_DELIVERY_MODE,
)
tenants.declare()


@receiver(post_save, sender=models.Tenant)
def post_save_tenant(sender, instance: models.Tenant, created: bool, **kwargs):
    action = 'create' if created else 'update'
    data = async_to_sync(response.Tenant.from_orm)(instance)
    body = DataChangeEvent(
        data=data.dict(by_alias=True),
        data_type='access.tenant',
        data_op=getattr(DataChangeEvent.DataOperation, action.upper()),
    )
    connection.ensure(tenants, tenants.publish)(
        message=body.json(),
        routing_key=f'v1.data.{action}',
    )


@receiver(post_save, sender=models.TenantCountry)
@receiver(post_delete, sender=models.TenantCountry)
def post_save_delete_tenant_country(sender, instance: models.TenantCountry, **kwargs):
    post_save_tenant(sender, instance=instance.tenant, created=False)


@receiver(post_delete, sender=models.Tenant)
def post_delete_tenant(sender, instance: models.Tenant, **kwargs):
    body = DataChangeEvent(
        data={
            'id': instance.id,
        },
        data_type='access.tenant',
        data_op=DataChangeEvent.DataOperation.DELETE,
    )
    connection.ensure(tenants, tenants.publish)(
        message=body.json(),
        routing_key='v1.data.delete',
    )
