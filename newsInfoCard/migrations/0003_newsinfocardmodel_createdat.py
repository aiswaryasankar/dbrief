# Generated by Django 3.2.9 on 2022-10-16 03:49

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsInfoCard', '0002_auto_20221016_0049'),
    ]

    operations = [
        migrations.AddField(
            model_name='newsinfocardmodel',
            name='createdAt',
            field=models.TextField(default=datetime.datetime.now, verbose_name='CreatedAt'),
        ),
    ]
