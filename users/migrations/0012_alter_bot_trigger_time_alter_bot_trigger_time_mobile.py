# Generated by Django 4.1.13 on 2024-10-05 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_bot_office_from_timing_bot_office_timezone_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bot',
            name='trigger_time',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='bot',
            name='trigger_time_mobile',
            field=models.IntegerField(),
        ),
    ]
