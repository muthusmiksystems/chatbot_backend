# Generated by Django 4.1.13 on 2024-10-07 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bots', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bot',
            name='trigger_time',
            field=models.CharField(blank=True, default=0, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='bot',
            name='trigger_time_mobile',
            field=models.CharField(default=0, max_length=500),
        ),
    ]
