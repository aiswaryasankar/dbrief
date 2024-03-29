# Generated by Django 3.2.9 on 2022-11-01 01:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LocationModel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('uuid', models.CharField(max_length=36, unique=True, verbose_name='UUID')),
                ('street', models.TextField(null=True, verbose_name='Street')),
                ('city', models.TextField(null=True, verbose_name='City')),
                ('state', models.TextField(null=True, verbose_name='State')),
                ('zip', models.TextField(null=True, verbose_name='Zip')),
                ('country', models.TextField(null=True, verbose_name='Country')),
            ],
        ),
        migrations.CreateModel(
            name='OrganizationCausesModel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('uuid', models.CharField(max_length=36, unique=True, verbose_name='UUID')),
                ('organizationUUID', models.CharField(max_length=36, verbose_name='OrganizationUUID')),
                ('cause', models.TextField(null=True, verbose_name='Cause')),
            ],
        ),
    ]
