# Generated by Django 3.2.9 on 2022-01-09 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userPreferences', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertopicmodel',
            name='forNewsletter',
            field=models.BooleanField(default=False, verbose_name='For Newsletter'),
        ),
    ]

