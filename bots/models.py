from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User
from django.conf import settings
# from django.utils import timezone
import jsonfield
# Create your models here.
class Bot(models.Model):
    BOT_TYPES = (
        ('chatbot', 'Chatbot'),
        ('voicebot', 'Voicebot'),
    )

    name = models.CharField(max_length=255)

    # customer_profile = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bots')
    customer_profile = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bots')
    avatar_url = models.URLField(max_length=500, blank=True, null=True)
    company_logo = models.ImageField(upload_to='company_logos/', blank=True, null=True, default='company_logos/default_logo.png')
    company_logo_url = models.URLField(max_length=500, blank=True, null=True)  
    bot_type = models.CharField(max_length=50, choices=BOT_TYPES)
    launcher_text = models.CharField(max_length=255, blank=True, null=True)
    to_emails = models.TextField(help_text='Comma-separated list of emails')
    trigger_time = models.CharField(default=0,blank=True,null=True,max_length=500)  # To store time in hours as an integer
    trigger_time_mobile = models.CharField(default=0,max_length=500)
    action = models.CharField(max_length=50,default=" ",null=True, blank=True)
    font_object = models.JSONField(default=dict, blank=True, null=True)  
    font = models.CharField(max_length=300, blank=True, null=True)
    font_size = models.CharField(max_length=10, blank=True, null=True, default="14px")
    theme = models.CharField(max_length=255, blank=True, null=True) 
    access_url_themes = models.URLField(max_length=500, blank=True, null=True)
    launcher_position = models.CharField(max_length=5, blank=True, null=True, default="RB")  
    view_setup_object = models.JSONField(default=dict, blank=True, null=True)  
    is_disabled = models.BooleanField(default=False)
    default_language = models.CharField(max_length=15, default='en', null=True, blank=True)
    multi_lingual_switch = models.BooleanField(default=False)
    language_code = models.CharField(max_length=15, default='en',)
    preference_statement = models.TextField(default="english")
    office_from_timing = models.TimeField(null=True, blank=True)
    office_to_timing = models.TimeField(null=True, blank=True)
    office_weekdays = jsonfield.JSONField(null=True, blank=True) 
    office_timezone = models.CharField(max_length=10, blank=True, null=True)
    whitelisted_urls = models.TextField(blank=True, null=True)  # Store URLs as comma-separated values
    blacklisted_urls = models.TextField(blank=True, null=True)
    banned_ips = models.TextField(blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    consent_enabled = models.BooleanField(default=False)
    consent_enabled_for_euro = models.BooleanField(default=False)
    consent_text = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)    
    

    class Meta:
        db_table="bot_create"

    def __str__(self):
        return self.name
    
class ChatbotQuestion(models.Model):
    chatbot_id = models.ForeignKey('Bot', on_delete=models.CASCADE) 
    question_text = models.TextField()
    sequence = models.IntegerField(auto_created=True)
    question_type = models.CharField(max_length=100)  # Avoiding 'type' to prevent conflict with Python's 'type' keyword.
    alternate_question_text = models.TextField(null=True, blank=True)
    auto_slide = models.CharField(max_length=10, default="0")
    default_options = models.TextField(null=True, blank=True)
    error_jump_question_id = models.IntegerField(null=True, blank=True)
    error_text = models.TextField(null=True, blank=True)
    flow_id = models.IntegerField(null=True, blank=True)
    image_url = models.URLField(null=True, blank=True)
    is_ai_available = models.CharField(max_length=10, default="0")
    is_feedback = models.CharField(max_length=10, default="0")
    is_set_dynamic = models.CharField(max_length=10, default="0")
    is_skip = models.CharField(max_length=10, default="0")
    logical_jump = models.CharField(max_length=10, default="0")
    next_question_id = models.IntegerField(null=True, blank=True)
    send_mail = models.CharField(max_length=10, default="0")
    sequence = models.IntegerField()
    session_variable_name = models.CharField(max_length=255, null=True, blank=True)
    xPos = models.CharField(max_length=10, null=True, blank=True)
    language = models.CharField(max_length=10, null=True, blank=True)
    yPos = models.CharField(max_length=10, null=True, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sequence'] 
        db_table="Questions"

    def save(self, *args, **kwargs):
        if not self.pk:
            max_sequence = ChatbotQuestion.objects.filter(chatbot_id=self.chatbot_id).aggregate(models.Max('sequence'))['sequence__max']
            self.sequence = (max_sequence or 0) + 1
        super().save(*args, **kwargs)

        def __str__(self):
            return f'{self.question_text} (Chatbot ID: {self.chatbot_id})'
        
class BotLanguage(models.Model):
    chatbot = models.ForeignKey(Bot, on_delete=models.CASCADE, related_name='languages')
    language_code = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.chatbot.name} - {self.language_code}"
    


class Agent(models.Model):
    agent_email = models.EmailField(unique=True)
    agent_name = models.CharField(max_length=255)
    agent_password = models.CharField(max_length=255)
    agent_id = models.IntegerField(unique=True,null=True,blank=True)
    agent_number = models.CharField(max_length=15, blank=True)
    livechat_redirect_whatsapp = models.BooleanField(default=False)
    agent_avatar = models.URLField(blank=True, null=True)
    chats_limit = models.IntegerField(default=5)
    department = models.ForeignKey('Bot', on_delete=models.CASCADE, related_name='agents_as_department')
    bots = models.ManyToManyField('Bot', related_name='agents')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.agent_name
