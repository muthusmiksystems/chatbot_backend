from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('__debug__/', include('debug_toolbar.urls')),
    path('api/', include('users.urls')), 
    path('api/', include('bots.urls')),  
]