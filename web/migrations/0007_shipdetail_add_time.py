# Generated by Django 2.2.2 on 2021-08-31 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0006_auto_20210831_1130'),
    ]

    operations = [
        migrations.AddField(
            model_name='shipdetail',
            name='add_time',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
