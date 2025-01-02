from rest_framework import serializers
from .models import *
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from datetime import datetime
import json
from rest_framework import serializers
import uuid

# class BotSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Bot
#         fields = '__all__'
#         extra_kwargs = {
#             'customer_profile': {'read_only': True},  # Set automatically from the authenticated user
#             'to_emails': {'read_only': True},  
#         }
    
#     def validate(self, data):
#         print("Data before validation:", data) 
#         return data

#     def create(self, validated_data):
#         request = self.context.get('request')
#         user = request.user

#         validated_data['to_emails'] = user.email
        
#         validated_data.pop('customer_profile', None)

#         # Assign 'customer_profile' from the request's authenticated user
#         bot = Bot.objects.create(customer_profile=self.context['request'].user, **validated_data)
#         return bot
    
# class BotStatusSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Bot
#         fields = ['id', 'is_disabled']


# class QuestionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ChatbotQuestion
#         fields = '__all__'
#         extra_kwargs = {
#             'sequence': {'required': False},
#         }

# class MultiLanguageUpdateSerializer(serializers.Serializer):
#     action = serializers.CharField(max_length=50)
#     chatbot_id = serializers.CharField(max_length=50)

#     # Fields for multi_lingual_switch action
#     multi_lingual_switch = serializers.CharField(max_length=1, required=False)

#     # Fields for language_setup action
#     language_code = serializers.CharField(max_length=5, required=False)

#     # Fields for add_language action
#     added_languages = serializers.ListField(child=serializers.CharField(max_length=10), required=False)
#     deleted_languages = serializers.ListField(child=serializers.CharField(max_length=10), required=False)

#     # Fields for multilingual_statement action
#     language_preference_statement = serializers.CharField(max_length=255, required=False)

#     def validate(self, data):
#         action = data.get('action')

#         if action == 'multi_lingual_switch':
#             if 'multi_lingual_switch' not in data:
#                 raise serializers.ValidationError({"multi_lingual_switch": "This field is required for multi_lingual_switch action."})
#         elif action == 'language_setup':
#             if 'language_code' not in data:
#                 raise serializers.ValidationError({"language_code": "This field is required for language_setup action."})
#         elif action == 'multilingual_statement':
#             if 'language_preference_statement' not in data:
#                 raise serializers.ValidationError({"language_preference_statement": "This field is required for multilingual_statement action."})
#         else:
#             raise serializers.ValidationError({"action": "Invalid action type."})

#         return data

# class LanguageUpdateSerializer(serializers.Serializer):
#     chatbot_id = serializers.CharField(max_length=50)
#     added_languages = serializers.ListField(child=serializers.CharField(max_length=10), required=False)
#     deleted_languages = serializers.ListField(child=serializers.CharField(max_length=10), required=False)

#     def validate(self, data):
#         if not data.get('added_languages') and not data.get('deleted_languages'):
#             raise serializers.ValidationError("At least one of added_languages or deleted_languages must be provided.")
#         return data


# class OfficeTimingsSerializer(serializers.Serializer):
#     chatbot_id = serializers.CharField(max_length=50)
#     office_timings = serializers.CharField(allow_blank=True)  # Allow an empty string

#     def validate_office_timings(self, value):
#         if value == "":  # If office_timings is empty, treat the bot as always active
#             return None  # You can also return a flag or custom structure if needed
        
#         try:
#             # Parse the office_timings string into a dictionary
#             office_timings_dict = json.loads(value)
#         except json.JSONDecodeError:
#             raise serializers.ValidationError("Invalid office_timings format. It should be a valid JSON string.")

#         # Validate the structure and fields of office_timings
#         required_keys = ['from_timing', 'to_timing', 'weekdays', 'timezone']
#         for key in required_keys:
#             if key not in office_timings_dict:
#                 raise serializers.ValidationError(f"{key} is required in office_timings.")

#         # Convert from 12-hour AM/PM format to 24-hour format
#         try:
#             from_time_24hr = datetime.strptime(office_timings_dict['from_timing'], '%I:%M %p').strftime('%H:%M')
#             to_time_24hr = datetime.strptime(office_timings_dict['to_timing'], '%I:%M %p').strftime('%H:%M')
#             office_timings_dict['from_timing'] = from_time_24hr
#             office_timings_dict['to_timing'] = to_time_24hr
#         except ValueError:
#             raise serializers.ValidationError("Time format should be 'HH:MM AM/PM'.")

#         # Ensure weekdays is a list of integers
#         if not isinstance(office_timings_dict['weekdays'], list) or \
#            not all(isinstance(day, int) for day in office_timings_dict['weekdays']):
#             raise serializers.ValidationError("weekdays must be a list of integers representing days of the week.")

#         return office_timings_dict  # Return the parsed and validated dictionary


# class TriggerTimeSetupSerializer(serializers.Serializer):
#     chatbot_id = serializers.CharField(max_length=50)
#     closure_enable = serializers.BooleanField(required=False)  # Optional field, defaults to False
#     trigger_time = serializers.IntegerField(min_value=1, max_value=24)  # Time in hours (assuming)
#     trigger_time_mobile = serializers.IntegerField(min_value=1, max_value=24)  # Time in hours (assuming)


# class AgentSerializer(serializers.ModelSerializer):
#     department = serializers.PrimaryKeyRelatedField(queryset=Bot.objects.all())
#     bots = serializers.PrimaryKeyRelatedField(queryset=Bot.objects.all(), many=True)

#     class Meta:
#         model = Agent
#         fields = [
#             'agent_email', 'agent_name', 'agent_password', 'agent_number', 
#             'livechat_redirect_whatsapp', 'agent_avatar', 'chats_limit', 
#             'department', 'bots'
#         ]
    
#     def create(self, validated_data):
#         # Extract password and other data
#         password = validated_data.pop('agent_password')
        
        
#         agent = Agent.objects.create(
#             agent_email=validated_data['agent_email'],
#             agent_name=validated_data['agent_name'],
#             agent_password=password, 
#             agent_number=validated_data['agent_number'],
#             livechat_redirect_whatsapp=validated_data['livechat_redirect_whatsapp'],
#             agent_avatar=validated_data['agent_avatar'],
#             chats_limit=validated_data['chats_limit'],
#             department=validated_data['department']
#         )
#         # Add bots to agent
#         bots = validated_data['bots']
#         agent.bots.set(bots)
#         return agent

from rest_framework import serializers
from .models import Bot, Agent, ChatbotQuestion
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.core.exceptions import ValidationError
import json
from users.models import User
from datetime import datetime
from bots.models import Counter
from bots.models import Bot,Counter


# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User  # Reference to your Django User model
#         fields = ['email', 'password', 'first_name', 'last_name','email', 'phone_number', 
#                   'company_name', 'company_address', 'company_url', 'contact_person', 
#                   'contact_number', 'contact_email', 'status', 'profile_img', 
#       
#             'OTP', 'otp_validation']
import uuid
from bson.objectid import ObjectId  
# from uuid import uuid4
class BotSerializer(serializers.Serializer):
    BOT_TYPES = [
        ('Lead', 'lead'),
        ('Support', 'support'),
    ]

    bot_id = serializers.IntegerField(required=False)  # Optional field
    name = serializers.CharField(max_length=255)
    customer_profile_id = serializers.CharField()
    to_emails = serializers.CharField(max_length=255)
    is_disabled = serializers.BooleanField(default=False)
    avatar_url = serializers.URLField(required=False, allow_null=True)
    company_logo_url = serializers.URLField(required=False, allow_null=True)
    bot_type = serializers.ChoiceField(choices=BOT_TYPES)
    font_object = serializers.JSONField(required=False, default=dict)
    view_setup_object = serializers.JSONField(required=False, default=dict)

    def create(self, validated_data):
        validated_data['bot_id'] = Bot.generate_bot_id()
        # super().create(validated_data)

        # Create and save the bot
        bot = Bot(**validated_data)
        bot.save()
        return bot


    
    def update(self, instance, validated_data):
        # Update fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def to_representation(self, instance):
        """
        Customize the serialized output.
        """
        data = super().to_representation(instance)
        return data
    
    



class BotStatusSerializer(serializers.Serializer):
    bot_id = serializers.CharField(read_only=True)
    is_disabled = serializers.BooleanField()


class QuestionSerializer(serializers.Serializer):
    bot_id = serializers.CharField()
    question_text = serializers.CharField(max_length=255)
    answer = serializers.CharField(max_length=1000, required=False)
    sequence = serializers.IntegerField(required=False, default=0)
    alternate_question_text = serializers.CharField(max_length=255, required=False)
    auto_slide = serializers.BooleanField(default=False)
    default_options = serializers.ListField(child=serializers.CharField(), required=False)
    error_jump_question_id = serializers.CharField(max_length=255, required=False)
    error_text = serializers.CharField(max_length=500, required=False)
    flow_id = serializers.CharField(max_length=255, required=False)
    image_url = serializers.URLField(required=False)
    is_ai_available = serializers.BooleanField(default=False)
    is_feedback = serializers.BooleanField(default=False)
    is_set_dynamic = serializers.BooleanField(default=False)
    is_skip = serializers.BooleanField(default=False)
    logical_jump = serializers.DictField(child=serializers.CharField(), required=False)
    next_question_id = serializers.CharField(max_length=255, required=False)
    send_mail = serializers.BooleanField(default=False)
    session_variable_name = serializers.CharField(max_length=255, required=False)
    xPos = serializers.IntegerField(required=False, default=0)
    yPos = serializers.IntegerField(required=False, default=0)
    status =serializers.BooleanField(default=False)

    def create(self, validated_data):
        return ChatbotQuestion.objects.create(**validated_data)

import json
from datetime import datetime
from rest_framework import serializers

class OfficeTimingsSerializer(serializers.Serializer):
    chatbot_id = serializers.CharField(max_length=50)
    office_timings = serializers.CharField(allow_blank=True)

    def validate_office_timings(self, value):
        if value == "":
            return None

        try:
            office_timings_dict = json.loads(value)
        except json.JSONDecodeError:
            raise serializers.ValidationError("Invalid office_timings format. It should be a valid JSON string.")

        required_keys = ['from_timing', 'to_timing', 'weekdays', 'timezone']
        for key in required_keys:
            if key not in office_timings_dict:
                raise serializers.ValidationError(f"{key} is required in office_timings.")

        try:
            from_time_24hr = datetime.strptime(office_timings_dict['from_timing'], '%I:%M %p').strftime('%H:%M')
            to_time_24hr = datetime.strptime(office_timings_dict['to_timing'], '%I:%M %p').strftime('%H:%M')
            office_timings_dict['from_timing'] = from_time_24hr
            office_timings_dict['to_timing'] = to_time_24hr

            if from_time_24hr >= to_time_24hr:
                raise serializers.ValidationError("'from_timing' must be earlier than 'to_timing'.")
        except ValueError:
            raise serializers.ValidationError("Time format should be 'HH:MM AM/PM'.")

        if not isinstance(office_timings_dict['weekdays'], list) or \
           not all(isinstance(day, int) and 1 <= day <= 7 for day in office_timings_dict['weekdays']):
            raise serializers.ValidationError("weekdays must be a list of integers (1 for Monday to 7 for Sunday).")

        return office_timings_dict



import re

class LanguageUpdateSerializer(serializers.Serializer):
    bot_id = serializers.CharField(max_length=50)
    added_languages = serializers.ListField(
        child=serializers.CharField(max_length=15), required=False
    )
    deleted_languages = serializers.ListField(
        child=serializers.CharField(max_length=15), required=False
    )

    def validate(self, data):
        if not data.get('added_languages') and not data.get('deleted_languages'):
            raise serializers.ValidationError(
                "At least one of added_languages or deleted_languages must be provided."
            )
        return data
    
class MultiLanguageUpdateSerializer(serializers.Serializer):
    action = serializers.CharField(max_length=50)
    bot_id = serializers.CharField(max_length=50)

    # Fields for multi_lingual_switch action
    multi_lingual_switch = serializers.CharField(max_length=1, required=False)

    # Fields for language_setup action
    language_code = serializers.CharField(max_length=5, required=False)

    # Fields for add_language action
    added_languages = serializers.ListField(child=serializers.CharField(max_length=10), required=False)
    deleted_languages = serializers.ListField(child=serializers.CharField(max_length=10), required=False)

    # Fields for multilingual_statement action
    language_preference_statement = serializers.CharField(max_length=255, required=False)

    def validate(self, data):
        action = data.get('action')

        if action == 'multi_lingual_switch':
            if 'multi_lingual_switch' not in data:
                raise serializers.ValidationError({"multi_lingual_switch": "This field is required for multi_lingual_switch action."})
        elif action == 'language_setup':
            if 'language_code' not in data:
                raise serializers.ValidationError({"language_code": "This field is required for language_setup action."})
        
        elif action == 'multilingual_statement':
            
            if 'language_preference_statement' not in data:
                raise serializers.ValidationError({"language_preference_statement": "This field is required for multilingual_statement action."})
        else:
            raise serializers.ValidationError({"action": "Invalid action type."})
        
        return data
    


class TriggerTimeSetupSerializer(serializers.Serializer):
    chatbot_id = serializers.CharField(max_length=50)
    closure_enable = serializers.BooleanField(required=False) 
    trigger_time = serializers.IntegerField(min_value=1, max_value=24)  
    trigger_time_mobile = serializers.IntegerField(min_value=1, max_value=24) 


class AgentSerializer(serializers.Serializer):
    agent_email = serializers.EmailField()
    agent_name = serializers.CharField(max_length=255)
    agent_password = serializers.CharField()
    agent_number = serializers.CharField(max_length=20)
    livechat_redirect_whatsapp = serializers.CharField(required=False)
    agent_avatar = serializers.ImageField(required=False)
    chats_limit = serializers.IntegerField(required=False)
    department = serializers.CharField()  # Bot ID reference
    bots = serializers.ListField(child=serializers.CharField())

    def create(self, validated_data):
        password = validated_data.pop('agent_password')
        
        agent = Agent.objects.create(
            agent_email=validated_data['agent_email'],
            agent_name=validated_data['agent_name'],
            agent_password=password, 
            agent_number=validated_data['agent_number'],
            livechat_redirect_whatsapp=validated_data['livechat_redirect_whatsapp'],
            agent_avatar=validated_data['agent_avatar'],
            chats_limit=validated_data['chats_limit'],
            department=validated_data['department']
        )
        bots = validated_data['bots']
        agent.bots.extend(bots)  
        return agent   
