# Generated by Django 4.0.5 on 2022-06-27 06:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bb_access', '0023_user_last_kafka_sync_at_user_updated_at'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='last_kafka_sync_at',
            new_name='last_kafka_publish_at',
        ),
    ]