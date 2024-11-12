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
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
import logging
import requests


logger = logging.getLogger(__name__)

class BotListCreateView(generics.ListCreateAPIView):
    queryset = Bot.objects.all()
    serializer_class = BotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Bot.objects.filter(customer_profile=self.request.user)

    def perform_create(self, serializer):
        serializer.save(customer_profile=self.request.user)
        serializer.save() 

    def create(self, request, *args, **kwargs):
        logger.debug(f"Incoming data: {request.data}")
        response = super().create(request, *args, **kwargs)
        logger.debug(f"Response data: {response.data}")

        # Customize the response to include a success message
        response.data = {
            "success": True,
            "message": "Bot created successfully!",
            "data": response.data
        }

        return response

class UserBotsView(ListAPIView):
    serializer_class = BotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Bot.objects.filter(customer_profile=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        # Customizing the response
        return Response({
            "status": True,
            "chatbot_details": serializer.data,
            "banned_ips": []  
        })
    

class BotStatusView(APIView):
    def post(self, request, *args, **kwargs):
        bot_id = request.data.get('id')
        
        try:
            # Retrieve the bot based on the ID
            bot = Bot.objects.get(id=bot_id)
            
            # Serialize the bot data
            serializer = BotStatusSerializer(bot)
            
            # Prepare the response data
            response_data = {
                "action": "bot_status_setup",
                "chatbot_id": bot_id,
                "is_disabled": "1" if bot.is_disabled else "0"
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Bot.DoesNotExist:
            return Response({"error": "Bot not found"}, status=status.HTTP_404_NOT_FOUND)



class BotDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        # Since DELETE requests usually don't carry a body, we can manually parse it
        bot_id = request.data.get('id')

        if not bot_id:
            return Response({"error": "Bot ID not provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Find the bot by its ID and make sure it belongs to the logged-in user
            bot = Bot.objects.get(id=bot_id, customer_profile=request.user)
        except Bot.DoesNotExist:
            return Response({"error": "Bot not found or you don't have permission to delete this bot"}, status=status.HTTP_404_NOT_FOUND)
        
        bot.delete()

        return Response({"message": f"Bot with ID {bot_id} deleted successfully"}, status=status.HTTP_200_OK)
    

class BotUpdateView(UpdateAPIView):
    queryset = Bot.objects.all()
    serializer_class = BotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Bot.objects.filter(customer_profile=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Log the update request
        logger.debug(f"Updating bot {instance.id} with data: {request.data}")

        # Set default values for the layout if they are not provided
        data = request.data.copy()
        data.setdefault('launcher_position', 'RB')
        data.setdefault('font_size', '14px')
        data.setdefault('theme', 'rgba(80, 93, 211, 1)..rgba(255, 255, 255, 1)..#ffffff..rgba(248, 248, 248, 1)..rgba(0, 118, 255, 1)..rgba(0, 118, 255, 1)')
        data.setdefault('view_setup_object', {
            "question_bubble_type": "2",
            "button_radius": "30",
            "bot_description": "",
            "main_opacity": 0,
            "button_text_alignment": "1",
            "button_border": "#3375b3",
            "bg_images": ""
        })

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "success": True,
            "message": "Bot updated successfully!",
            "data": serializer.data
        })
    

logger = logging.getLogger(__name__)


class DuplicateChatbotView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        # Fetching the chatbot_id from the query params
        chatbot_id = request.query_params.get('chatbot_id')
        new_name = request.query_params.get('chatbot_name')  # New name for the duplicated bot

        if not chatbot_id:
            return Response({"error": "chatbot_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Try to fetch the chatbot to duplicate
        try:
            chatbot = Bot.objects.get(id=chatbot_id, customer_profile=request.user)
        except Bot.DoesNotExist:
            return Response({"error": "Chatbot not found or you do not have permission to duplicate this bot"}, status=status.HTTP_404_NOT_FOUND)

        # Create the new bot as a copy of the old one
        chatbot.pk = None  # Reset the primary key to None to create a new object
        chatbot.name = new_name if new_name else f"{chatbot.name}_copy"  # Set new name or append '_copy'
        chatbot.save()

        logger.info(f"Chatbot duplicated: original_id={chatbot_id}, new_id={chatbot.id}")

        # Return the new chatbot ID in the response
        return Response({
            "status": True,
            "message": "Chatbot duplicated successfully",
            "new_chatbot_id": chatbot.id
        }, status=status.HTTP_201_CREATED)


class ChatbotQuestionCreateView(APIView):
    permission_classes = [IsAuthenticated] 
    def post(self, request):
        # Deserialize the incoming data
        serializer = QuestionSerializer(data=request.data)
        
        # Validate the data
        if serializer.is_valid():
            # Save the valid data to the database
            question = serializer.save()
            
            # Prepare the response data
            response_data = {
                "question_details": {
                    "id": question.id,
                    "question_text": question.question_text,
                    "type": question.question_type,
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

            # Return a success response
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        # Return a bad request response if validation fails
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class MultiLanguageUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MultiLanguageUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            action = serializer.validated_data['action']
            chatbot_id = serializer.validated_data['chatbot_id']

            try:
                chatbot = Bot.objects.get(id=chatbot_id)
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

            # Handle "add_language"
            elif action == 'add_language':
                added_languages = serializer.validated_data.get('added_languages', [])
                deleted_languages = serializer.validated_data.get('deleted_languages', [])

                # Add new languages
                for lang_code in added_languages:
                    Bot.objects.get_or_create(chatbot=chatbot, language_code=lang_code)

                # Remove deleted languages
                for lang_code in deleted_languages:
                    Bot.objects.filter(chatbot=chatbot, language_code=lang_code).delete()

                return Response({"status": "Languages updated successfully"}, status=status.HTTP_200_OK)

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
        # Deserialize the request data
        serializer = LanguageUpdateSerializer(data=request.data)

        # Validate the request data
        if serializer.is_valid():
            chatbot_id = serializer.validated_data['chatbot_id']
            added_languages = serializer.validated_data.get('added_languages', [])
            deleted_languages = serializer.validated_data.get('deleted_languages', [])

            try:
                # Check if the chatbot exists
                chatbot = Bot.objects.get(id=chatbot_id)
            except Bot.DoesNotExist:
                return Response({"error": "Chatbot not found."}, status=status.HTTP_404_NOT_FOUND)

            # Add new languages
            for lang_code in added_languages:
                BotLanguage.objects.get_or_create(chatbot=chatbot, language_code=lang_code)

            # Delete languages
            for lang_code in deleted_languages:
                BotLanguage.objects.filter(chatbot=chatbot, language_code=lang_code).delete()

            # Return success response
            return Response({"status": True}, status=status.HTTP_200_OK)

        # If the request is invalid, return validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UpdateOfficeTimingsView(APIView):
    def post(self, request):
        serializer = OfficeTimingsSerializer(data=request.data)
        if serializer.is_valid():
            chatbot_id = serializer.validated_data['chatbot_id']
            office_timings = serializer.validated_data.get('office_timings')

            try:
                # Fetch the chatbot by its ID
                chatbot = Bot.objects.get(id=chatbot_id)
            except Bot.DoesNotExist:
                return Response({"error": "Chatbot not found."}, status=status.HTTP_404_NOT_FOUND)

            if office_timings is None:
                # If office_timings is None, set the bot as always active (you can customize the logic)
                chatbot.office_from_timing = None  # or a special value to indicate "always active"
                chatbot.office_to_timing = None
                chatbot.office_weekdays = None  # or set a flag like "always_active" to True
                chatbot.save()
            else:
                # Update the chatbot's office timings
                chatbot.office_from_timing = office_timings['from_timing']
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


class UpdateChatbotURLsView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        action = request.data.get('action')
        chatbot_id = request.data.get('chatbot_id')
        urls = request.data.get('whitelisting_urls') or request.data.get('blacklisting_urls')

        if not action or not chatbot_id or not urls:
            return Response({"error": "Missing required parameters"}, status=status.HTTP_400_BAD_REQUEST)

        # Get the chatbot instance
        chatbot = get_object_or_404(Bot, id=chatbot_id)

        if action == "whitelisting_urls_setup":
            # Whitelisting action
            chatbot.whitelisted_urls = urls
            chatbot.save()
            return Response({"status": True}, status=status.HTTP_200_OK)

        elif action == "blacklisting_urls_setup":
            # Blacklisting action
            chatbot.blacklisted_urls = urls
            chatbot.save()
            return Response({"status": True}, status=status.HTTP_200_OK)

        else:
            return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)


class UpdateChatbotPlatformsView(APIView):

    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        action = request.data.get('action')
        chatbot_id = request.data.get('chatbot_id')
        platforms = request.data.get('available_platforms')
        ip_address = request.data.get('ip_address')
        reason = request.data.get('reason', 'No reason provided')  # Default reason if not provided
        consent_enabled = request.data.get('consent_enabled')
        consent_enabled_for_euro = request.data.get('consent_enabled_for_euro')
        consent_text = request.data.get('consent_text')
        

        if not action or not chatbot_id :
            return Response({"error": "Missing required parameters"}, status=status.HTTP_400_BAD_REQUEST)

        chatbot = get_object_or_404(Bot, id=chatbot_id)

        if action == "available_platforms":
            # Update available platforms for the chatbot
            chatbot.available_platforms = platforms
            chatbot.save()
            return Response({"status": True}, status=status.HTTP_200_OK)
        
        elif action == "ban":
            # Ban the IP address
            banned_ips = chatbot.banned_ips.split(',') if chatbot.banned_ips else []
            
            if ip_address not in banned_ips:
                banned_ips.append(ip_address)
                chatbot.banned_ips = ','.join(banned_ips)
                chatbot.save()

            return Response({"msg": "IP banned", "status": True}, status=status.HTTP_200_OK)

        elif action == "unban":
            # Unban the IP address
            banned_ips = chatbot.banned_ips.split(',') if chatbot.banned_ips else []
            
            if ip_address in banned_ips:
                banned_ips.remove(ip_address)
                chatbot.banned_ips = ','.join(banned_ips)
                chatbot.save()

            return Response({"msg": "IP unbanned", "status": True}, status=status.HTTP_200_OK)
        
        elif action =="consent_status_setup":
            chatbot.consent_enabled = bool(int(consent_enabled))  # Convert "1" or "0" to boolean
            chatbot.consent_enabled_for_euro = bool(int(consent_enabled_for_euro))  # Convert "1" or "0" to boolean
            chatbot.consent_text = consent_text
            chatbot.save()

            return Response({"status": True}, status=status.HTTP_200_OK)

        else:
            return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)



class DepartmentView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        department_name = request.data.get('department_name')
        action = request.data.get('action')
        customer_profile_id = request.data.get('customer_profile_id') 
        department_id = request.data.get('department_id') # Make sure to get this from the request

        if not department_name or not customer_profile_id:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        if action == "add":
            try:
                # Create a new department with customer_profile_id
                department = Bot.objects.create(name=department_name, customer_profile_id=customer_profile_id)
                return Response({"msg": "Department successfully created", "status": True}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        elif action == "update":
            if not department_name or not department_id:
                return Response({"error": "Missing department_name or department_id"}, status=status.HTTP_400_BAD_REQUEST)

            # Get the department by ID
            try:
                department = Bot.objects.get(id=department_id)

            except Bot.DoesNotExist:
                return Response({"error": "Department not found"}, status=status.HTTP_404_NOT_FOUND)

            # Update the department name
            department.name = department_name
            department.save()

            return Response({"msg": "Department successfully updated", "status": True}, status=status.HTTP_200_OK)
        
        elif action =="delete":
            if not department_id:
                return Response({"error": "Department ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            department = get_object_or_404(Bot, id=department_id)  # Or any other unique identifier
        
            department.delete()

            return Response({"msg": "Department successfully deleted", "status": True}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)


class AgentSignupView(APIView):

    def post(self, request, *args, **kwargs):
        # Check the recaptcha_response
        recaptcha_response = request.data.get('recaptcha_response')
        # if not self.verify_recaptcha(recaptcha_response):
        #     return Response({"status": False, "msg": "Invalid reCAPTCHA"}, status=status.HTTP_400_BAD_REQUEST)

        # Process signup data
        serializer = AgentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": True, "msg": "Agent created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def verify_recaptcha(self, recaptcha_response):
       
        recaptcha_url = "https://www.google.com/recaptcha/api/siteverify"
        recaptcha_secret = '6LdN42QqAAAAAOPhr4Ay13aX9ksTOYv5I9kJNMFy'  # replace with your reCAPTCHA secret key

        data = {
            'secret': recaptcha_secret,
            'response': recaptcha_response
        }

        response = requests.post(recaptcha_url, data=data)
        result = response.json()
        return result.get('success', False)
    


class AgentUpdateView(APIView):
    """
    API to handle agent update.
    """

    def post(self, request, *args, **kwargs):
        # Check reCAPTCHA response
        # recaptcha_response = request.data.get('recaptcha_response')
        # if not self.verify_recaptcha(recaptcha_response):
    #    /\     return Response({"status": False, "msg": "Invalid reCAPTCHA"}, status=status.HTTP_400_BAD_REQUEST)

        # Get agent_id from the request data
        agent_id = request.data.get('agent_id')
        if not agent_id:
            return Response({"status": False, "msg": "Agent ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the agent object to update
        try:
            agent = Agent.objects.get(id=agent_id)
        except Agent.DoesNotExist:
            return Response({"status": False, "msg": "Agent not found"}, status=status.HTTP_404_NOT_FOUND)

        # Use serializer to update the agent
        serializer = AgentUpdateSerializer(agent, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": True, "msg": "Agent updated successfully"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def verify_recaptcha(self, recaptcha_response):
        recaptcha_url = "https://www.google.com/recaptcha/api/siteverify"
        recaptcha_secret = '6LdN42QqAAAAAOPhr4Ay13aX9ksTOYv5I9kJNMFy'  # Replace with your actual secret key

        data = {
            'secret': recaptcha_secret,
            'response': recaptcha_response
        }

        response = requests.post(recaptcha_url, data=data)
        result = response.json()

        return result.get('success', False)
