# Generated by Django 3.2.9 on 2022-01-10 01:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsletter', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsletterconfigmodel',
            name='userId',
            field=models.IntegerField(unique=True, verbose_name='UserId'),
        ),
    ]
