# Generated by Django 3.2.9 on 2022-03-06 05:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsletter', '0002_alter_newsletterconfigmodel_userid'),
    ]

    operations = [
        migrations.AddField(
            model_name='newsletterconfigmodel',
            name='firebaseUserId',
            field=models.TextField(null=True, verbose_name='FirebaseUserId'),
        ),
    ]
