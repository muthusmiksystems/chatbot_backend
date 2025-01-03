from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

urlpatterns = [
    path('bots/', BotListCreateView.as_view(), name='bot-list-create'),
    path('bots_list/', UserBotsView.as_view(), name='user_bots'),
    path('status/', BotStatusView.as_view(), name='bot-status'),
    path('delete/', BotDeleteView.as_view(), name='bot-delete'),
    path('<int:bot_id>/update/', BotUpdateView.as_view(), name='bot-update'),
    path('duplicate-bot/', DuplicateChatbotView.as_view(), name='duplicate-bot'),
    path('create-question/', ChatbotQuestionCreateView.as_view(), name='create-question'),
    path('language-update/', MultiLanguageUpdateView.as_view(), name='multi_language_update'),
    path('update-languages/', LanguageUpdateView.as_view(), name='update_languages'),
    path('update-office-timings/', UpdateOfficeTimingsView.as_view(), name='update_office_timings'),
    path('auto-trigger-setup/', AutoTriggerSetupView.as_view(), name='auto_trigger_setup'),
    path('update-urls/', UpdateChatbotURLsView.as_view(), name='update-urls'),
    path('update-platforms/', UpdateChatbotPlatformsView.as_view(), name='update-platforms'),
    path('department/', DepartmentView.as_view(), name='department'),
    path('agents_signup/', AgentSignupView.as_view(), name='agent-signup'),
    path('save_contact/', SaveContact.as_view(), name='agent-signup'),
]

