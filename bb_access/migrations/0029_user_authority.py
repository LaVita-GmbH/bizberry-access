# Generated by Django 4.1 on 2023-04-20 10:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bb_access', '0028_user_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='authority',
            field=models.CharField(choices=[('BIZBERRY', 'Bizberry'), ('OSHOP', 'Oshop')], default='BIZBERRY', max_length=12),
        ),
    ]