# Generated by Django 3.2.9 on 2021-12-31 21:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('topicModeling', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topicmodel',
            name='parentTopic',
            field=models.CharField(max_length=255, verbose_name='Parent topic'),
        ),
        migrations.AlterField(
            model_name='topicmodel',
            name='topic',
            field=models.CharField(max_length=255, verbose_name='Topic'),
        ),
        migrations.AlterUniqueTogether(
            name='topicmodel',
            unique_together={('topic', 'parentTopic')},
        ),
    ]