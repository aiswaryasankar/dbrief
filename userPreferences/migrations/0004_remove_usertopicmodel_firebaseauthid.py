# Generated by Django 3.2.9 on 2022-06-16 03:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userPreferences', '0003_usertopicmodel_firebaseauthid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usertopicmodel',
            name='firebaseAuthId',
        ),
    ]