# Generated by Django 5.1.1 on 2024-10-09 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bots', '0003_bot_blacklisted_urls_bot_whitelisted_urls'),
    ]

    operations = [
        migrations.AddField(
            model_name='bot',
            name='banned_ips',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='bot',
            name='reason',
            field=models.TextField(blank=True, null=True),
        ),
    ]