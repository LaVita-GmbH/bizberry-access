# Generated by Django 3.1.1 on 2021-01-20 14:50

from django.db import migrations, models
import bb_access.models.tenant


class Migration(migrations.Migration):

    dependencies = [
        ('bb_access', '0009_auto_20201214_1018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tenantcountry',
            name='id',
            field=models.CharField(default=bb_access.models.tenant._default_tenant_country_id, editable=False, max_length=24, primary_key=True, serialize=False),
        ),
    ]
