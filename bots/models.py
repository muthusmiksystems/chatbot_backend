from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User
from django.conf import settings
from uuid import uuid4
# from django.utils import timezone
from django.contrib.auth import get_user_model
import jsonfield
from mongoengine import Document, StringField, ReferenceField, BooleanField, DateTimeField, ListField, URLField, ImageField, DictField, IntField, EmailField
from django.conf import settings
import jsonfield
from mongoengine import connect
from mongoengine.errors import DoesNotExist
from mongoengine import Document, StringField, IntField, BooleanField, DateTimeField, DictField, URLField, ListField
from datetime import datetime

# Connect to the database
connect('bot_mongo2', host='mongodb://localhost:27017/bot_mongo2')
User = get_user_model()

# def get_next_sequence(counter_name):
#     """
#     Fetch the next sequence value for the given counter.
#     """
#     try:
#         # Try to find an existing Counter document
#         counter = Counter.objects.get(name=counter_name)
#         counter.sequence += 1
#         counter.save()
#     except DoesNotExist:
#         # If it doesn't exist, create a new Counter document
#         counter = Counter(name=counter_name, sequence=1)
#         counter.save()
#     return counter.sequence


from mongoengine import (
    Document,
    IntField,
    StringField,
    URLField,
    BooleanField,
    DateTimeField,
    DictField,
    ListField,
    ImageField,
)

class Counter(Document):
    collection_name = StringField(required=True, unique=True)
    seq = IntField(default=0)

    @classmethod
    def get_next_sequence(cls, collection_name):
        counter = cls.objects(collection_name=collection_name).modify(
            upsert=True, new=True, inc__seq=1
        )
        return counter.seq

class Bot(Document):
    
    bot_id = IntField(unique=True, required=False)  # Based on "id" 
    name = StringField(max_length=255)  # Based on "name"
    customer_profile_id = StringField(max_length=255)  # Based on "customer_profile_id"
    launcher_text = StringField(max_length=255)  # Based on "launcher_text"
    access_url_themes = StringField(max_length=500)  # Based on "access_url_themes"
    access_url_uploaded_background = URLField(max_length=500, blank=True, null=True)  # Based on "access_url_uploaded_background"
    adwords_integration = StringField(max_length=10)  # Based on "adwords_integration"
    analytics_logo = URLField(blank=True, null=True)  # Based on "analytics_logo"
    available_platforms = StringField(max_length=255)  # Based on "available_platforms"
    avatar_url = URLField(max_length=500)  # Based on "avatar_url"
    bg_color = StringField(max_length=50)  # Based on "bg_color"
    bg_image = URLField(blank=True, null=True)  # Based on "bg_image"
    blacklisting_urls = ListField(StringField(), blank=True, null=True)  # Based on "blacklisting_urls"
    bot_type = StringField(max_length=50)  # Based on "bot_type"
    closure_enable = StringField(max_length=10)  # Based on "closure_enable"
    company_emails_only = BooleanField(default=False)  # Based on "company_emails_only"
    company_logo_url = URLField(blank=True, null=True)  # Based on "company_logo_url"
    company_name = StringField(max_length=255)  # Based on "company_name"
    consent_enabled = BooleanField(default=False)  # Based on "consent_enabled"
    consent_enabled_for_euro = BooleanField(default=False)  # Based on "consent_enabled_for_euro"
    consent_text = StringField(blank=True, null=True)  # Based on "consent_text"
    created_at = DateTimeField(auto_now_add=True)  # Based on "created_at"
    custom_brand_enabled = BooleanField(default=False)  # Based on "custom_brand_enabled"
    custom_brand_name = StringField(max_length=255, blank=True, null=True)  # Based on "custom_brand_name"
    custom_brand_url = URLField(blank=True, null=True)  # Based on "custom_brand_url"
    custom_settings = DictField(default=dict, blank=True, null=True)  # Based on "custom_settings"
    delay_switch = StringField(max_length=10)  # Based on "delay_switch"
    df_access_token = StringField(max_length=255, blank=True, null=True)  # Based on "df_access_token"
    email_otp_vali = BooleanField(default=False)  # Based on "email_otp_vali"
    enable_live_online = StringField(max_length=10)  # Based on "enable_live_online"
    end_point = URLField(blank=True, null=True)  # Based on "end_point"
    font = StringField(max_length=500)  # Based on "font"
    font_object = DictField(default=dict, blank=True, null=True)  # Based on "font_object"
    font_size = StringField(max_length=50, default="14px")  # Based on "font_size"
    ga_tracking_id = StringField(max_length=255, blank=True, null=True)  # Based on "ga_tracking_id"
    is_data_masking = BooleanField(default=False)  # Based on "is_data_masking"
    is_disabled = BooleanField(default=False)  # Based on "is_disabled"
    is_toured = BooleanField(default=False)  # Based on "is_toured"
    language_code = StringField(max_length=15, default="en")  # Based on "language_code"
    launcher_position = StringField(max_length=5, default="RB")  # Based on "launcher_position"
    lead_acknowledge_subject = StringField(max_length=255, blank=True, null=True)  # Based on "lead_acknowledge_subject"
    lead_acknowledge_template = StringField(max_length=500, blank=True, null=True)  # Based on "lead_acknowledge_template"
    lead_email_template = StringField(max_length=255, blank=True, null=True)  # Based on "lead_email_template"
    lead_revisit_notification = BooleanField(default=False)  # Based on "lead_revisit_notification"
    lead_unfilled_alert = BooleanField(default=False)  # Based on "lead_unfilled_alert"
    live_chat = StringField(blank=True, null=True)  # Based on "live_chat"
    live_chat_active = BooleanField(default=False)  # Based on "live_chat_active"
    live_chat_notification_sound = BooleanField(default=False)  # Based on "live_chat_notification_sound"
    multi_lingual_switch = BooleanField(default=False)  # Based on "multi_lingual_switch"
    multilingual_statement = StringField(blank=True, null=True)  # Based on "multilingual_statement"
    notifcation_phone_number = StringField(blank=True, null=True)  # Based on "notifcation_phone_number"
    notification_sound_enabled = BooleanField(default=False)  # Based on "notification_sound_enabled"
    office_timings = DictField(blank=True, null=True)  # Based on "office_timings"
    phone_validation = BooleanField(default=False)  # Based on "phone_validation"
    properties = DictField(default=dict, blank=True, null=True)  # Based on "properties"
    remove_branding = BooleanField(default=False)  # Based on "remove_branding"
    return_text = StringField(blank=True, null=True)  # Based on "return_text"
    revisit_switch = BooleanField(default=False)  # Based on "revisit_switch"
    save_contact = BooleanField(default=False)  # Based on "save_contact"
    sender_email = StringField(blank=True, null=True)  # Based on "sender_email"
    skip_otp_validation = BooleanField(default=False)  # Based on "skip_otp_validation"
    spreadsheet_id = StringField(blank=True, null=True)  # Based on "spreadsheet_id"
    spreadsheet_url = URLField(blank=True, null=True)  # Based on "spreadsheet_url"
    stop_redirection = BooleanField(default=False)  # Based on "stop_redirection"
    store_session = BooleanField(default=False)  # Based on "store_session"
    text_to_speech_status = BooleanField(default=False)  # Based on "text_to_speech_status"
    text_to_speech_voice = StringField(blank=True, null=True)  # Based on "text_to_speech_voice"
    theme = StringField(max_length=500)  # Based on "theme"
    profile_id =StringField(max_length=500,default=bot_id,blank=True)
    time_delay = StringField(max_length=10)  # Based on "time_delay"
    to_emails = StringField(blank=True, null=True)  # Based on "to_emails"
    trigger_time = StringField(max_length=10)  # Based on "trigger_time"
    trigger_time_mobile = StringField(max_length=10)  # Based on "trigger_time_mobile"
    uploaded_avatar_url = URLField(blank=True, null=True)  # Based on "uploaded_avatar_url"
    view_setup_object = DictField(default=dict, blank=True, null=True)  # Based on "view_setup_object"
    voice_input = BooleanField(default=False)  # Based on "voice_input"
    whatsapp_notification_number = StringField(blank=True, null=True)  # Based on "whatsapp_notification_number"
    whatsapp_otp_val = StringField(blank=True, null=True)  # Based on "whatsapp_otp_val"
    whitelisted_urls = ListField(StringField(), blank=True, null=True)  # Based on "whitelisted_urls"
    zapier_webhook = StringField(blank=True, null=True)  # Based on "zapier_webhook"

    meta = {
        'db_alias': 'bots_db',  # MongoDB alias
        'collection': 'bots',  # MongoDB collection
    }

    def __str__(self):
        return self.name

    @classmethod
    def generate_bot_id(cls):
        return Counter.get_next_sequence("bots")




class ChatbotQuestion(Document):
    bot_id = StringField(required=True)
    question_text = StringField(max_length=255, required=True)
    answer = StringField(max_length=1000, required=False)
    sequence = IntField(required=False, default=0)
    alternate_question_text = StringField(max_length=255, required=False)
    auto_slide = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    default_options = ListField(default=list)  
    error_jump_question_id = StringField(max_length=255, required=False)
    error_text = StringField(max_length=500, required=False)
    flow_id = StringField(max_length=255, required=False)
    image_url = URLField(required=False)
    is_ai_available = BooleanField(default=False)
    is_feedback = BooleanField(default=False)
    is_set_dynamic = BooleanField(default=False)
    is_skip = BooleanField(default=False)
    logical_jump = DictField(default=dict)
    next_question_id = StringField(max_length=255, required=False)
    send_mail = BooleanField(default=False)
    session_variable_name = StringField(max_length=255, required=False)
    xPos = IntField(required=False, default=0)
    yPos = IntField(required=False, default=0)
    status = BooleanField(default=False)

    meta = {
        'db_alias': 'bots_db',
        'collection': 'questions'
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super(ChatbotQuestion, self).save(*args, **kwargs)


class BotLanguage(Document):
    chatbot = ReferenceField('Bot', required=True)
    language_code = StringField(max_length=15, required=True)

    meta = {
        'db_alias': 'bots_db',
        'collection': 'bot_languages',
        'indexes': [
            {'fields': ('chatbot', 'language_code'), 'unique': True}
        ]
    }

    def __str__(self):
        return f"{self.chatbot.name} - {self.language_code}"

class Agent(Document):
    agent_email = EmailField(unique=True)
    agent_name = StringField(max_length=255)
    agent_password = StringField(max_length=255)
    agent_number = StringField(max_length=15, blank=True)
    livechat_redirect_whatsapp = BooleanField(default=False)
    agent_avatar = URLField(blank=True, null=True)
    chats_limit = IntField(default=5)
    department = ReferenceField(Bot, reverse_delete_rule='CASCADE')
    bots = ListField(ReferenceField(Bot))
    created_at = DateTimeField(auto_now_add=True)


    meta = {
        'db_alias': 'bots_db', 
        'collection': 'bots',  
    }

    def __str__(self):
        return self.agent_name
    

# class Counter(Document):
#     name = StringField(required=True, unique=True)  # Counter name
#     sequence = IntField(default=0)  # Current sequence value

#     meta = {
#         'db_alias': 'bots_db',  
#         'collection': 'counters'
#     }
# from mongoengine import Document, StringField, IntField
# import logger

# class Counter(Document):
#     collection_name = StringField(required=True, unique=True)
#     sequence = IntField(default=0)

#     meta = {
#         'db_alias': 'bots_db',
#         'collection': 'counters',  # Collection to store counters
#     }


#     @classmethod
#     def get_next_sequence(cls, collection_name):
#         """
#         Atomically increments and returns the next sequence number for a collection.
#         """
#         # try:
#         counter = cls.objects(collection_name=collection_name).modify(
#             upsert=True,  # Create a new document if it doesn't exist
#             new=True,  # Return the updated document                set_on_insert={"sequence": 0},  # Initialize `sequence` if creating
#             inc__sequence=1  # Increment the `sequence` field
#         )

#         if not counter:
#                 # Fallback: Create the counter manually
#             counter = cls(collection_name=collection_name, sequence=1)
#             counter.save()
#             return counter.sequence
#         else:
#             raise ValueError(f"Failed to get sequence for {collection_name}")

#         # except Exception as e:
#         #     # logger.error(
#         #     #     f"Error in get_next_sequence for {collection_name}: {str(e)}",
#         #     #     exc_info=True  # Logs the stack trace
#         #     # )
#         #     # raise
#             # pass
