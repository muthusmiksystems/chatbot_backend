# Generated by Django 4.1.13 on 2024-10-05 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_alter_bot_trigger_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bot',
            name='trigger_time',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='bot',
            name='trigger_time_mobile',
            field=models.IntegerField(default=0),
        ),
    ]
