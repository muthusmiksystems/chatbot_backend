from rest_framework import serializers
from .models import *
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from datetime import datetime
import json

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email', None)
        password = data.get('password', None)

        if email is None or password is None:
            raise serializers.ValidationError('An email address and password are required.')

        user = authenticate(username=email, password=password)

        if user is None:
            raise AuthenticationFailed('Invalid email or password.')

        if not user.is_active:
            raise AuthenticationFailed('This account is inactive.')

        return {
            'user': user,
        }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'phone_number', 
                  'company_name', 'company_address', 'company_url', 'contact_person', 
                  'contact_number', 'contact_email', 'status', 'profile_img', 
                  'OTP', 'otp_validation']
        extra_kwargs = {
            'password': {'write_only': True},  # Ensure the password is not returned in responses
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # Hash the password
        user.save()
        return user
    
class ChangePasswordSerializer(serializers.Serializer):
    action = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, data):
        # Check if action is "update_password"
        if data.get('action') != 'update_password':
            raise serializers.ValidationError({"action": "Invalid action."})
        
        # Check if new_password matches new_password_confirm
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "Passwords do not match."})
        
        # Validate the strength of the new password
        try:
            validate_password(data['new_password'])
        except ValidationError as e:
            raise serializers.ValidationError({"new_password": e.messages})
        
        return data



