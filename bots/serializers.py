from rest_framework import serializers
from .models import *
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from datetime import datetime
import json
from rest_framework import serializers


class BotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bot

        fields = '__all__'
        extra_kwargs = {
            'customer_profile': {'read_only': True},  # Set automatically from the authenticated user
            'to_emails': {'read_only': True},  
        }
    
    def validate(self, data):
        print("Data before validation:", data) 
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user

        validated_data['to_emails'] = user.email
        
        validated_data.pop('customer_profile', None)

        # Assign 'customer_profile' from the request's authenticated user
        bot = Bot.objects.create(customer_profile=self.context['request'].user, **validated_data)
        return bot
    
class BotStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bot
        fields = ['id', 'is_disabled']


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatbotQuestion
        fields = '__all__'
        extra_kwargs = {
            'sequence': {'required': False},
        }

class MultiLanguageUpdateSerializer(serializers.Serializer):
    action = serializers.CharField(max_length=50)
    chatbot_id = serializers.CharField(max_length=50)

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

class LanguageUpdateSerializer(serializers.Serializer):
    chatbot_id = serializers.CharField(max_length=50)
    added_languages = serializers.ListField(child=serializers.CharField(max_length=10), required=False)
    deleted_languages = serializers.ListField(child=serializers.CharField(max_length=10), required=False)

    def validate(self, data):
        if not data.get('added_languages') and not data.get('deleted_languages'):
            raise serializers.ValidationError("At least one of added_languages or deleted_languages must be provided.")
        return data


class OfficeTimingsSerializer(serializers.Serializer):
    chatbot_id = serializers.CharField(max_length=50)
    office_timings = serializers.CharField(allow_blank=True)  # Allow an empty string

    def validate_office_timings(self, value):
        if value == "":  # If office_timings is empty, treat the bot as always active
            return None  # You can also return a flag or custom structure if needed
        
        try:
            # Parse the office_timings string into a dictionary
            office_timings_dict = json.loads(value)
        except json.JSONDecodeError:
            raise serializers.ValidationError("Invalid office_timings format. It should be a valid JSON string.")

        # Validate the structure and fields of office_timings
        required_keys = ['from_timing', 'to_timing', 'weekdays', 'timezone']
        for key in required_keys:
            if key not in office_timings_dict:
                raise serializers.ValidationError(f"{key} is required in office_timings.")

        # Convert from 12-hour AM/PM format to 24-hour format
        try:
            from_time_24hr = datetime.strptime(office_timings_dict['from_timing'], '%I:%M %p').strftime('%H:%M')
            to_time_24hr = datetime.strptime(office_timings_dict['to_timing'], '%I:%M %p').strftime('%H:%M')
            office_timings_dict['from_timing'] = from_time_24hr
            office_timings_dict['to_timing'] = to_time_24hr
        except ValueError:
            raise serializers.ValidationError("Time format should be 'HH:MM AM/PM'.")

        # Ensure weekdays is a list of integers
        if not isinstance(office_timings_dict['weekdays'], list) or \
           not all(isinstance(day, int) for day in office_timings_dict['weekdays']):
            raise serializers.ValidationError("weekdays must be a list of integers representing days of the week.")

        return office_timings_dict  # Return the parsed and validated dictionary


class TriggerTimeSetupSerializer(serializers.Serializer):
    chatbot_id = serializers.CharField(max_length=50)
    closure_enable = serializers.BooleanField(required=False)  # Optional field, defaults to False
    trigger_time = serializers.IntegerField(min_value=1, max_value=24)  # Time in hours (assuming)
    trigger_time_mobile = serializers.IntegerField(min_value=1, max_value=24)  # Time in hours (assuming)