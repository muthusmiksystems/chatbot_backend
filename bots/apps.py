# # bots/apps.py
# from django.apps import AppConfig
# from mongoengine import connect, disconnect
# from django.conf import settings

# class BotsConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'bots'

#     def ready(self):
#         from django.conf import settings
#         # Disconnect any existing 'default' connection
#         disconnect(alias='default')

#         # Connect to MongoDB
#         mongo_settings = settings.MONGODB_SETTINGS
#         connect(
#             db=mongo_settings['db'],
#             host=mongo_settings['host'],
#             port=mongo_settings['port'],
#             alias='bots_db'
#         )
        
# bots/apps.py
from django.apps import AppConfig
from mongoengine import connect, disconnect
from django.conf import settings

class BotsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bots'

    def ready(self):
        """
        Initialize MongoDB connection with 'bots_db' alias.
        """
        # Disconnect any existing connection for this alias
        disconnect(alias='bots_db')

        # Fetch MongoDB settings from settings.py
        mongo_settings = settings.MONGODB_SETTINGS

        # Connect to MongoDB with the 'bots_db' alias
        connect(
            db=mongo_settings.get('db', 'default_db_name'),
            host=mongo_settings.get('host', 'localhost'),
            port=mongo_settings.get('port', 27017),
            alias=mongo_settings.get('alias', 'bots_db')  # Use 'bots_db' alias explicitly
        )

