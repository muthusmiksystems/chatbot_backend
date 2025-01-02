# from django.shortcuts import render
from .models import User
from .serializers import BotSerializer,MultiLanguageUpdateSerializer
from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status, permissions
from rest_framework.generics import ListAPIView,UpdateAPIView
from rest_framework.response import Response
from .serializers import *
from .models import Bot
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
import logging
from mongoengine import connect, disconnect

from urllib.parse import urlparse
import requests


logger = logging.getLogger(__name__)

class BotListCreateView(generics.ListCreateAPIView):
    serializer_class = BotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_identifier = str(self.request.user.id)  # Adjust based on your schema
        return Bot.objects.filter(customer_profile_id=user_identifier)

    def perform_create(self, serializer):
        customer_profile_id = str(self.request.user.id)  # Or self.request.user.email if applicable
        try:
            serializer.save(customer_profile_id=customer_profile_id)
        except Exception as e:
            logger.error(f"Error during bot creation: {e}")
            raise

    def create(self, request, *args, **kwargs):
        logger.debug(f"Incoming data for bot creation: {request.data}")
        response = super().create(request, *args, **kwargs)
        logger.debug(f"Response after creation: {response.data}")
        return response

            # return Response(response.data, status=response.status_code)
        

        

class UserBotsView(ListAPIView):
    serializer_class = BotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try:
            # Filter bots created by the logged-in user based on customer_profile_id
            customer_profile_id = str(self.request.user.id)  # Adjust this if using email
            return Bot.objects.filter(customer_profile_id=customer_profile_id)
        except Exception as e:
            logger.error(f"Error retrieving bots: {e}")
            return Bot.objects.none()  # Return an empty queryset on failure

    def list(self, request, *args, **kwargs):
        try:
            # Get the filtered queryset
            queryset = self.get_queryset()

            # Serialize the queryset
            serializer = self.get_serializer(queryset, many=True)

            # Calculate the count of bots for the user
            bot_count = queryset.count()

            # Customize the response
            return Response({
                "status": True,
                "chatbot_count": bot_count,
                "chatbot_details": serializer.data,
                "banned_ips": []  # Provide additional data if necessary
            })
        except Exception as e:
            logger.error(f"Error in list view: {e}")
            return Response({
                "status": False,
                "message": "An error occurred while retrieving bots."
            }, status=500)


class BotStatusView(APIView):
    def post(self, request, *args, **kwargs):
        bot_id = request.data.get('bot_id')
        
        if not bot_id:
            return Response({
                "status": False,
                "message": "bot_id is required."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Retrieve the bot using bot_id
            bot = Bot.objects.get(bot_id=bot_id)
            
            # Use the serializer to format the bot data (optional)
            serializer = BotStatusSerializer(bot)
            
            response_data = {
                "status": True,
                "action": "bot_status_setup",
                "chatbot_id": bot_id,
                "is_disabled": bot.is_disabled  # Return as a boolean for better API usability
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Bot.DoesNotExist:
            logger.error(f"Bot with bot_id {bot_id} not found.")
            return Response({
                "status": False,
                "message": "Bot not found."
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return Response({
                "status": False,
                "message": "An error occurred while retrieving the bot status."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class BotDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        bot_id = request.data.get('bot_id')

        # Validate that bot_id is provided
        if not bot_id:
            return Response({
                "status": False,
                "message": "Bot ID not provided."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the bot by bot_id
            bot = Bot.objects.get(bot_id=bot_id)

            # Check if the bot belongs to the authenticated user
            if bot.customer_profile_id != str(request.user.id):
                return Response({
                    "status": False,
                    "message": "You don't have permission to delete this bot."
                }, status=status.HTTP_403_FORBIDDEN)

            # Delete the bot
            bot.delete()

            logger.info(f"Bot with ID {bot_id} deleted successfully.")
            return Response({
                "status": True,
                "message": f"Bot with ID {bot_id} deleted successfully."
            }, status=status.HTTP_200_OK)

        except Bot.DoesNotExist:
            logger.error(f"Bot with ID {bot_id} not found.")
            return Response({
                "status": False,
                "message": "Bot not found."
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"An unexpected error occurred while deleting bot {bot_id}: {e}")
            return Response({
                "status": False,
                "message": "An error occurred while trying to delete the bot."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    

logger = logging.getLogger(__name__)

from django.shortcuts import get_object_or_404
from users.models import User  

class BotUpdateView(UpdateAPIView):
    serializer_class = BotSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "bot_id"

    def get_queryset(self):
        # Filter bots for the logged-in user
        user_identifier = str(self.request.user.id)  # Replace with email if required
        return Bot.objects.filter(customer_profile_id=user_identifier)

    def update(self, request, *args, **kwargs):
        bot_id = kwargs.get(self.lookup_field)

        # Debug log for incoming request
        logger.debug(f"Request to update bot with ID {bot_id}: {request.data}")

        try:
            # Retrieve the Bot instance
            instance = self.get_queryset().get(bot_id=bot_id)
        except Bot.DoesNotExist:
            logger.error(f"Bot with ID {bot_id} not found for user {request.user.id}.")
            raise NotFound({"status": False, "message": "Bot not found"})

        # Allow partial updates
        partial = kwargs.pop('partial', True)

        # Deserialize and validate the incoming data
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # Perform the update
        self.perform_update(serializer)

        # Debug log for successful update
        logger.info(f"Bot with ID {bot_id} updated successfully.")

        # Customize the response
        return Response({
            "status": True,
            "message": "Bot updated successfully!",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        # Save the updated bot instance
        serializer.save()


import copy

# class DuplicateChatbotView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         # Extract query parameters
#         chatbot_id = request.query_params.get('chatbot_id')
#         chatbot_name = request.query_params.get('chatbot_name')
#         profile_id = request.query_params.get('profile_id')

#         if not chatbot_id or not chatbot_name:
#             return Response({
#                 "status": False,
#                 "message": "chatbot_id and chatbot_name are required."
#             }, status=400)

#         try:
#             # Fetch the bot to be duplicated
#             original_bot = Bot.objects.get(bot_id=int(chatbot_id))
#         except Bot.DoesNotExist:
#             raise NotFound({"status": False, "message": "Bot not found."})

#         # Duplicate the bot
#         new_bot_data = copy.deepcopy(original_bot.to_mongo().to_dict())
#         new_bot_data.pop('_id')  # Remove the MongoDB ID to allow for a new document
#         new_bot_data['bot_id'] = Counter.get_next_sequence('bot_id')  # Generate a new bot ID
#         new_bot_data['name'] = chatbot_name
#         if profile_id:
#             new_bot_data['profile_id'] = profile_id  # Optionally set the profile ID

#         # Create the new bot
#         new_bot = Bot(**new_bot_data)
#         new_bot.save()

#         return Response({
#             "status": True,
#             "message": f"new chatbot_id {new_bot.bot_id}"
#         }, status=200)



class DuplicateChatbotView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Extract query parameters
        chatbot_id = request.data.get('chatbot_id')
        chatbot_name = request.data.get('chatbot_name')
        profile_id = request.data.get('profile_id')

        if not chatbot_id or not chatbot_name:
            return Response({
                "status": False,
                "message": "chatbot_id and chatbot_name is required."
            }, status=400)

        try:
            # Fetch the bot to be duplicated
            original_bot = Bot.objects.get(bot_id=int(chatbot_id))
        except Bot.DoesNotExist:
            logger.error(f"Bot with bot_id {chatbot_id} not found.")
            raise NotFound({"status": False, "message": "Bot not found."})

        # Duplicate the bot
        try:
            new_bot_data = copy.deepcopy(original_bot.to_mongo().to_dict())
            new_bot_data.pop('_id')  # Remove the MongoDB ID to allow for a new document
            # new_bot_data['bot_id'] = Counter.get_next_sequence('bot_id')  # Generate a new bot ID
            new_bot_data['name'] = chatbot_name
            if profile_id:
                new_bot_data['profile_id'] = profile_id  # Optionally set the profile ID

            # Create the new bot
            new_bot = Bot(**new_bot_data)
            new_bot.save()

            logger.info(f"Successfully duplicated bot with new bot_id: {new_bot.bot_id}")

            return Response({
                "status": True,
                "message": f"New chatbot created with chatbot_id {new_bot.bot_id}",
                "data": {
                    "bot_id": new_bot.bot_id,
                    "name": new_bot.name,
                    "profile_id": new_bot.profile_id if 'profile_id' in new_bot_data else None
                }
            }, status=200)

        except Exception as e:
            v=logger.error(f"Error duplicating bot with bot_id {chatbot_id}: {e}")
            print("==========>>>>>>>>>",v)
            return Response({
                "status": False,
                
                "message": "An error occurred while duplicating on bot."
            }, status=500)

    
class ChatbotQuestionCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():
            question = serializer.save()

            response_data = {
                "status": True,
                "message": "Question created successfully.",
                "question_details": {
                    "id": str(question.id),
                    "question_text": question.question_text,
                    "type": question.status,
                    "alternate_question_text": question.alternate_question_text,
                    "auto_slide": question.auto_slide,
                    "created_at": question.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    "default_options": question.default_options,
                    "error_jump_question_id": question.error_jump_question_id,
                    "error_text": question.error_text,
                    "flow_id": question.flow_id,
                    "image_url": question.image_url,
                    "is_ai_available": question.is_ai_available,
                    "is_feedback": question.is_feedback,
                    "is_set_dynamic": question.is_set_dynamic,
                    "is_skip": question.is_skip,
                    "logical_jump": question.logical_jump,
                    "next_question_id": question.next_question_id,
                    "send_mail": question.send_mail,
                    "sequence": question.sequence,
                    "session_variable_name": question.session_variable_name,
                    "updated_at": question.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                    "xPos": question.xPos,
                    "yPos": question.yPos,
                    "status": question.status
                }
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MultiLanguageUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MultiLanguageUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            action = serializer.validated_data['action']
            chatbot_id = serializer.validated_data['bot_id']

            try:
                chatbot = Bot.objects.get(bot_id=chatbot_id)
            except Bot.DoesNotExist:
                return Response({"error": "Chatbot not found."}, status=status.HTTP_404_NOT_FOUND)

            # Handle "multi_lingual_switch"
            if action == 'multi_lingual_switch':
                chatbot.multi_lingual_switch = serializer.validated_data['multi_lingual_switch'] == '1'
                chatbot.save()
                return Response({"status": "Multi-lingual switch updated successfully"}, status=status.HTTP_200_OK)

            # Handle "language_setup"
            elif action == 'language_setup':
                chatbot.default_language = serializer.validated_data['language_code']
                chatbot.save()
                return Response({"status": "Default language set successfully"}, status=status.HTTP_200_OK)

            # # Handle "add_language"
            # elif action == 'add_language':
            #     added_languages = serializer.validated_data.get('added_languages', [])
            #     deleted_languages = serializer.validated_data.get('deleted_languages', [])

            #     # Add new languages
            #     for lang_code in added_languages:
            #         Bot.objects.get_or_create(chatbot=chatbot, language_code=lang_code)

            #     # Remove deleted languages
            #     for lang_code in deleted_languages:
            #         Bot.objects.filter(chatbot=chatbot, language_code=lang_code).delete()

            #     return Response({"status": "Languages updated successfully"}, status=status.HTTP_200_OK)

            # Handle "multilingual_statement"
            elif action == 'multilingual_statement':
                preference, created = Bot.objects.get_or_create(chatbot=chatbot)
                preference.preference_statement = serializer.validated_data['language_preference_statement']
                preference.save()
                return Response({"status": "Language preference statement updated successfully"}, status=status.HTTP_200_OK)

        # If the data is not valid, return the error response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LanguageUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LanguageUpdateSerializer(data=request.data)

        if serializer.is_valid():
            chatbot_id = serializer.validated_data['bot_id']
            added_languages = serializer.validated_data.get('added_languages', [])
            deleted_languages = serializer.validated_data.get('deleted_languages', [])

            # Check if the chatbot exists
            try:
                chatbot = Bot.objects.get(bot_id=chatbot_id)
            except Bot.DoesNotExist:
                return Response({"error": "Chatbot not found."}, status=status.HTTP_404_NOT_FOUND)

            # Add new languages
            for lang_code in added_languages:
                if not BotLanguage.objects.filter(chatbot=chatbot, language_code=lang_code).first():
                    BotLanguage(chatbot=chatbot, language_code=lang_code).save()

            # Delete specified languages
            BotLanguage.objects.filter(chatbot=chatbot, language_code__in=deleted_languages).delete()

            # Retrieve updated list of languages
            current_languages = [
                lang.language_code for lang in BotLanguage.objects.filter(chatbot=chatbot)
            ]

            return Response(
                {
                    "status": True,
                    "message": "Languages updated successfully.",
                    "current_languages": current_languages,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    

from datetime import datetime

class UpdateOfficeTimingsView(APIView):
    def post(self, request):
        serializer = OfficeTimingsSerializer(data=request.data)
        if serializer.is_valid():
            chatbot_id = serializer.validated_data['chatbot_id']
            office_timings = serializer.validated_data.get('office_timings')

            try:
                chatbot = Bot.objects.get(bot_id=chatbot_id)
            except Bot.DoesNotExist:
                return Response({"error": "Chatbot not found."}, status=status.HTTP_404_NOT_FOUND)

            if office_timings is None:
                # Mark bot as always active
                chatbot.office_from_timing = None
                chatbot.office_to_timing = None
                chatbot.office_weekdays = None
            else:
                chatbot.office_from_timing = office_timings['from_timing']  # Already converted to "HH:MM"
                chatbot.office_to_timing = office_timings['to_timing']
                chatbot.office_weekdays = office_timings['weekdays']
                chatbot.office_timezone = office_timings['timezone']

            chatbot.save()
            return Response({"status": True}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class AutoTriggerSetupView(APIView):
    def post(self, request):
        serializer = TriggerTimeSetupSerializer(data=request.data)
        
        if serializer.is_valid():
            chatbot_id = serializer.validated_data['chatbot_id']
            trigger_time = serializer.validated_data['trigger_time']
            trigger_time_mobile = serializer.validated_data['trigger_time_mobile']
            closure_enable = serializer.validated_data.get('closure_enable', False)  # Defaults to False if not provided
            
            try:
                # Fetch the chatbot by its ID
                chatbot = Bot.objects.get(id=chatbot_id)
            except Bot.DoesNotExist:
                return Response({"error": "Chatbot not found."}, status=status.HTTP_404_NOT_FOUND)

            # Update the trigger times
            chatbot.trigger_time = trigger_time
            chatbot.trigger_time_mobile = trigger_time_mobile

            # Update the closure_enable if provided (you can customize how closure_enable affects the bot)
            if closure_enable is not None:
                chatbot.closure_enable = closure_enable
            
            chatbot.save()  # Save the updated values

            # Return a success response
            return Response({"status": True}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from mongoengine.errors import DoesNotExist

class UpdateChatbotURLsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        action = request.data.get('action')
        chatbot_id = request.data.get('chatbot_id')
        urls = request.data.get('whitelisting_urls') or request.data.get('blacklisting_urls')

        if not action or not chatbot_id or urls is None:
            return Response({"error": "Missing required parameters"}, status=status.HTTP_400_BAD_REQUEST)

        if action not in ["whitelisting_urls_setup", "blacklisting_urls_setup"]:
            return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate URLs (if provided as JSON string, parse it)
        try:
            if isinstance(urls, str):
                urls = json.loads(urls)
            if not isinstance(urls, list) or not all(isinstance(url, str) for url in urls):
                raise ValueError
        except (json.JSONDecodeError, ValueError):
            return Response({"error": "Invalid URL format. Provide a list of strings."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the chatbot instance using MongoEngine
        try:
            chatbot = Bot.objects.get(bot_id=chatbot_id)
        except DoesNotExist:
            return Response({"error": "Chatbot not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            if action == "whitelisting_urls_setup":
                # Whitelisting action
                chatbot.whitelisted_urls = urls
            elif action == "blacklisting_urls_setup":
                # Blacklisting action
                chatbot.blacklisted_urls = urls

            chatbot.save()
            return Response({"status": True, "message": "URLs updated successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateChatbotPlatformsView(APIView):

    permission_classes = [IsAuthenticated]

    def get_bot(self, chatbot_id):
        """Helper function to retrieve a bot or return an error."""
        try:
            return Bot.objects.get(bot_id=chatbot_id)
        except Bot.DoesNotExist:
            return None

    def convert_to_boolean(self, value):
        """Helper function to safely convert '1' or '0' to boolean."""
        return bool(int(value)) if value is not None else False

    def post(self, request, *args, **kwargs):
        action = request.data.get('action')
        chatbot_id = request.data.get('chatbot_id')
        platforms = request.data.get('available_platforms')
        ip_address = request.data.get('ip_address')
        reason = request.data.get('reason', 'No reason provided')  # Default reason if not provided
        consent_enabled = request.data.get('consent_enabled')
        consent_enabled_for_euro = request.data.get('consent_enabled_for_euro')
        consent_text = request.data.get('consent_text')
        is_disabled = request.data.get('is_disabled')
        lead_unfilled_alert = request.data.get('lead_unfilled_alert')
        live_chat_notification_sound = request.data.get('live_chat_notification_sound')
        notification_sound_enabled = request.data.get('notification_sound_enabled')
        voice_input = request.data.get('voice_input')
        email_otp = request.data.get('email_otp')
        store_session = request.data.get('store_session')
        adwords_integration = request.data.get('adwords_integration')
        delay_switch = request.data.get('delay_switch')
        revisit_switch = request.data.get('revisit_switch')
        lead_revisit_notification = request.data.get('lead_revisit_notification')

        if not action or not chatbot_id:
            return Response({"error": "Missing required parameters"}, status=status.HTTP_400_BAD_REQUEST)

        chatbot = self.get_bot(chatbot_id)
        if not chatbot:
            return Response({"error": "Bot not found"}, status=status.HTTP_404_NOT_FOUND)

        if action == "available_platforms":
            # Update available platforms for the chatbot
            chatbot.available_platforms = platforms
            chatbot.save()
            return Response({"status": True}, status=status.HTTP_200_OK)

        elif action == "ban":
            banned_ips = chatbot.banned_ips.split(',') if chatbot.banned_ips else []
            if ip_address not in banned_ips:
                banned_ips.append(ip_address)
                chatbot.banned_ips = ','.join(banned_ips)
                chatbot.save()

            return Response({"msg": "IP banned", "status": True}, status=status.HTTP_200_OK)

        elif action == "unban":
            banned_ips = chatbot.banned_ips.split(',') if chatbot.banned_ips else []
            if ip_address in banned_ips:
                banned_ips.remove(ip_address)
                chatbot.banned_ips = ','.join(banned_ips)
                chatbot.save()

            return Response({"msg": "IP unbanned", "status": True}, status=status.HTTP_200_OK)

        elif action == "consent_status_setup":
            chatbot.consent_enabled = self.convert_to_boolean(consent_enabled)
            chatbot.consent_enabled_for_euro = self.convert_to_boolean(consent_enabled_for_euro)
            chatbot.consent_text = consent_text
            chatbot.save()
            return Response({"status": True}, status=status.HTTP_200_OK)

        elif action == "bot_status_setup":
            chatbot.is_disabled = self.convert_to_boolean(is_disabled)
            chatbot.save()
            return Response({"status": True}, status=status.HTTP_200_OK)

        elif action == "revisit_switch_setup":
            chatbot.is_disabled = self.convert_to_boolean(revisit_switch)
            chatbot.save()
            return Response({"status": True}, status=status.HTTP_200_OK)

        elif action == "lead_revisit_notification_setup":
            chatbot.is_disabled = self.convert_to_boolean(lead_revisit_notification)
            chatbot.save()
            return Response({"status": True}, status=status.HTTP_200_OK)

        elif action == "store_session":
            chatbot.is_disabled = self.convert_to_boolean(store_session)
            chatbot.save()
            return Response({"status": True}, status=status.HTTP_200_OK)

        elif action == "lead_unfilled_alert":
            chatbot.is_disabled = self.convert_to_boolean(lead_unfilled_alert)
            chatbot.save()
            return Response({"status": True}, status=status.HTTP_200_OK)

        elif action == "email_otp":
            chatbot.is_disabled = self.convert_to_boolean(email_otp)
            chatbot.save()
            return Response({"status": True}, status=status.HTTP_200_OK)

        elif action == "voice_input":
            chatbot.is_disabled = self.convert_to_boolean(voice_input)
            chatbot.save()
            return Response({"status": True}, status=status.HTTP_200_OK)

        elif action == "live_chat_notification_sound":
            chatbot.is_disabled = self.convert_to_boolean(live_chat_notification_sound)
            chatbot.save()
            return Response({"status": True}, status=status.HTTP_200_OK)

        elif action == "notification_sound_enabled":
            chatbot.is_disabled = self.convert_to_boolean(notification_sound_enabled)
            chatbot.save()
            return Response({"status": True}, status=status.HTTP_200_OK)

        elif action == "adwords_integration":
            chatbot.is_disabled = self.convert_to_boolean(adwords_integration)
            chatbot.save()
            return Response({"status": True}, status=status.HTTP_200_OK)

        elif action == "delay_in_responses_setup":
            chatbot.is_disabled = self.convert_to_boolean(delay_switch)
            chatbot.save()
            return Response({"status": True}, status=status.HTTP_200_OK)

        else:
            return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)







class SaveContact(APIView):
    
    permission_classes=[IsAuthenticated]

    def post(self, request, *args, **kwargs):
        chatbot_id = request.data.get('chatbot_id')
        enable=request.data.get('enable')
        # chatbot_id = get_object_or_404(Bot, id=chatbot_id)
        if not chatbot_id :
            return Response({"error": "Missing required parameters"}, status=status.HTTP_400_BAD_REQUEST)

        # chatbot_id = get_object_or_404(Bot, id=chatbot_id)
        try:
            bot = Bot.objects.get(id=chatbot_id)
        except Bot.DoesNotExist:
            return Response({"error": "Bot not found"}, status=status.HTTP_404_NOT_FOUND)

        bot.is_disabled = bool(int(enable))  # Convert "1" or "0" to boolean
        bot.save()
        return Response({"status": True}, status=status.HTTP_200_OK)

        









class DepartmentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        action = request.data.get('action')
        department_name = request.data.get('department_name')
        user_id = request.data.get('customer_profile_id')  # Retrieve the user ID from the request
        bot_id = request.data.get('bot_id')  # For identifying a specific bot/department

        if not action:
            return Response({"error": "Action is required"}, status=status.HTTP_400_BAD_REQUEST)

        if action == "add":
            # Validate required fields
            if not department_name or not user_id:
                return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # Create a new Bot (department)
                department = Bot.objects.create(
                    bot_id=self.get_next_sequence('bot_id'),  # Generate a unique bot ID
                    name=department_name,
                    user=user_id,
                )
                return Response(
                    {"msg": "Department successfully created", "status": True, "data": department.to_json()},
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        elif action == "update":
            # Validate required fields
            if not bot_id or not department_name:
                return Response(
                    {"error": "Missing bot_id or department_name"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                # Update the Bot (department) name
                department = Bot.objects.get(bot_id=bot_id)
                department.name = department_name
                department.save()
                return Response(
                    {"msg": "Department successfully updated", "status": True},
                    status=status.HTTP_200_OK,
                )
            except Bot.DoesNotExist:
                return Response({"error": "Department not found"}, status=status.HTTP_404_NOT_FOUND)

        elif action == "delete":
            if not bot_id:
                return Response(
                    {"error": "bot_id is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                # Delete the Bot (department)
                department = Bot.objects.get(bot_id=bot_id)
                department.delete()
                return Response(
                    {"msg": "Department successfully deleted", "status": True},
                    status=status.HTTP_200_OK,
                )
            except Bot.DoesNotExist:
                return Response({"error": "Department not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

    # def get_next_sequence(self, counter_name):
    #     """
    #     Helper method to generate a unique bot_id using the Counter model.
    #     """
    #     counter, created = Counter.objects.get_or_create(name=counter_name)
    #     counter.sequence += 1
    #     counter.save()
    #     return counter.sequence



class AgentSignupView(APIView):
    def post(self, request, *args, **kwargs):
       
        recaptcha_response = request.data.get('recaptcha_response')
        # if not self.verify_recaptcha(recaptcha_response):
        #     return Response({"status": False, "msg": "Invalid reCAPTCHA"}, status=status.HTTP_400_BAD_REQUEST)

        action = request.data.get('action')
        if action == 'edit':
            return self.update_agent(request)
        else:
            return self.create_agent(request)

    def create_agent(self, request):
        # Process agent creation
        serializer = AgentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": True, "msg": "Agent created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update_agent(self, request):
        # Extract agent_id from the request to identify which agent to update
        agent_id = request.data.get('agent_id')
        try:
            agent = Agent.objects.get(agent_id=agent_id)
        except Agent.DoesNotExist:
            return Response({"status": False, "msg": "Agent not found"}, status=status.HTTP_404_NOT_FOUND)

        # Process the update
        serializer = AgentSerializer(agent, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": True, "msg": "Agent updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


