# Generated by Django 4.1.13 on 2024-10-05 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_alter_bot_trigger_time_alter_bot_trigger_time_mobile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bot',
            name='trigger_time',
            field=models.IntegerField(max_length=200),
        ),
    ]
