# Generated by Django 4.1.13 on 2024-10-03 15:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_bot_action_bot_default_language_bot_language_code_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chatbotquestion',
            old_name='chatbot',
            new_name='chatbot_id',
        ),
    ]