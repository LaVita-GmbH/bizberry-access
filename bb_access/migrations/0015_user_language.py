# Generated by Django 3.1.1 on 2021-02-23 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bb_access', '0014_auto_20210222_1005'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='language',
            field=models.CharField(default='de', max_length=8),
            preserve_default=False,
        ),
    ]
