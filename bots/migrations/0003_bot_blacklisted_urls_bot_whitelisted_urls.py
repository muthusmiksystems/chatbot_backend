# Generated by Django 5.1.1 on 2024-10-08 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bots', '0002_alter_bot_trigger_time_alter_bot_trigger_time_mobile'),
    ]

    operations = [
        migrations.AddField(
            model_name='bot',
            name='blacklisted_urls',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='bot',
            name='whitelisted_urls',
            field=models.TextField(blank=True, null=True),
        ),
    ]