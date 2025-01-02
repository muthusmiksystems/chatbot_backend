from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework import status

class BotCreationTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='johndoe',
            email='johndoe@example.com',
            password='yourpassword'
        )
        self.client = APIClient()
        self.client.login(username='johndoe', password='yourpassword')
        self.token_url = reverse('token_obtain_pair')

        # Get JWT token
        response = self.client.post(self.token_url, {'email': 'johndoe@example.com', 'password': 'yourpassword'}, format='json')
        self.access_token = response.data['access']

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        self.bot_url = reverse('bot-list')  # Assuming you have named the view 'bot-list'

    def test_create_bot(self):
        data = {
            "name": "Customer Support Bot",
            "bot_type": "customer_support",
            "launcher_text": "Hello! How can I assist you today?",
            "to_emails": "support@example.com",
            "trigger_time": "2024-09-04T12:00:00Z",
            "trigger_time_mobile": "2024-09-04T12:00:00Z",
            "font_object": {"font-family": "Arial", "font-size": "12px"},
            "font": "Arial",
            "theme": "light",
            "access_url_themes": "http://example.com/theme",
            "description": "A bot to assist customers with their inquiries.",
            "is_active": True
        }

        response = self.client.post(self.bot_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['message'], 'Bot created successfully!')
        self.assertEqual(response.data['data']['name'], 'Customer Support Bot')
