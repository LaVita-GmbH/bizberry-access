# Generated by Django 3.1.1 on 2021-02-22 09:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bb_access', '0012_auto_20210219_1226'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='roles',
        ),
        migrations.RemoveField(
            model_name='useraccesstoken',
            name='tenant',
        ),
        migrations.RemoveField(
            model_name='usertoken',
            name='tenant',
        ),
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users', to='bb_access.role'),
        ),
        migrations.DeleteModel(
            name='UserRoleRelation',
        ),
    ]