# Generated by Django 3.1.1 on 2020-11-16 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bb_access', '0003_auto_20201113_1402'),
    ]

    operations = [
        migrations.AddField(
            model_name='scope',
            name='is_critical',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='scope',
            name='is_internal',
            field=models.BooleanField(default=False),
        ),
    ]