# Generated by Django 2.2.2 on 2021-08-31 11:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0005_auto_20210830_2349'),
    ]

    operations = [
        migrations.AddField(
            model_name='shipdetail',
            name='ship',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ship_detail', to='web.Ship'),
        ),
        migrations.AddField(
            model_name='shipdetail',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='web.UserInfo'),
        ),
        migrations.AlterField(
            model_name='shipdetail',
            name='file',
            field=models.FileField(upload_to='file/'),
        ),
    ]
