# Generated by Django 5.1 on 2024-09-24 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_bot_company_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='bot',
            name='company_logo_url',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='bot',
            name='font_size',
            field=models.CharField(blank=True, default='14px', max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='bot',
            name='launcher_position',
            field=models.CharField(blank=True, default='RB', max_length=5, null=True),
        ),
        migrations.AddField(
            model_name='bot',
            name='view_setup_object',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AlterField(
            model_name='bot',
            name='theme',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
