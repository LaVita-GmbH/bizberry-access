from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from djfapi.utils.sentry import capture_exception
from djpykafka.events.publish import EventPublisher, DataChangePublisher
from ... import models
from ...schemas import response
from . import connection


class TenantPublisher(
    DataChangePublisher,
    EventPublisher,
    orm_model=models.Tenant,
    event_schema=response.Tenant,
    connection=connection,
    topic='bizberry.access.tenants',
    data_type='access.tenant',
    is_changed_included=True,
):
    pass


@receiver(post_save, sender=models.TenantCountry)
@receiver(post_delete, sender=models.TenantCountry)
@capture_exception
def post_save_delete_tenant_country(sender, instance: models.TenantCountry, **kwargs):
    TenantPublisher.handle(sender, instance=instance.tenant, created=False)
