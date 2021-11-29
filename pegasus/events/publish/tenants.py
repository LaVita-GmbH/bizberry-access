import json
from kombu import Exchange
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from olympus.schemas import DataChangeEvent
from olympus.utils.pydantic_django import transfer_from_orm
from olympus.utils.django import on_transaction_complete
from olympus.utils.sentry import capture_exception
from ... import models
from ...schemas import response
from . import connection


channel = connection.channel()
tenants = Exchange(
    name='olymp.access.tenants',
    type='topic',
    durable=True,
    channel=channel,
    delivery_mode=Exchange.PERSISTENT_DELIVERY_MODE,
)
tenants.declare()


@receiver(post_save, sender=models.Tenant)
@capture_exception
@on_transaction_complete()
def post_save_tenant(sender, instance: models.Tenant, created: bool, **kwargs):
    action = 'create' if created else 'update'
    data = transfer_from_orm(response.Tenant, instance)
    body = DataChangeEvent(
        data=data.dict(by_alias=True),
        data_type='access.tenant',
        data_op=getattr(DataChangeEvent.DataOperation, action.upper()),
    )
    connection.Producer(exchange=tenants).publish(
        retry=True,
        retry_policy={'max_retries': 3},
        body=body.json(),
        content_type='application/json',
        routing_key=f'v1.data.{action}',
    )


@receiver(post_save, sender=models.TenantCountry)
@receiver(post_delete, sender=models.TenantCountry)
@capture_exception
def post_save_delete_tenant_country(sender, instance: models.TenantCountry, **kwargs):
    post_save_tenant(sender, instance=instance.tenant, created=False)


@receiver(post_delete, sender=models.Tenant)
@on_transaction_complete()
def post_delete_tenant(sender, instance: models.Tenant, **kwargs):
    body = DataChangeEvent(
        data={
            'id': instance.id,
        },
        data_type='access.tenant',
        data_op=DataChangeEvent.DataOperation.DELETE,
    )
    connection.Producer(exchange=tenants).publish(
        retry=True,
        retry_policy={'max_retries': 3},
        body=body.json(),
        content_type='application/json',
        routing_key='v1.data.delete',
    )
