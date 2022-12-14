# Generated by Django 4.0.7 on 2022-08-17 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bb_access', '0026_user_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='gender',
            field=models.CharField(blank=True, choices=[('MALE', 'Male'), ('FEMALE', 'Female'), ('OTHER', 'Other')], max_length=8, null=True),
        ),
        migrations.AddField(
            model_name='userotp',
            name='last_kafka_publish_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userotp',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
