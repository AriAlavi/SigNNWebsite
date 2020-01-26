from django.urls import path, include
from django.contrib.auth import views as auth_views
import main.views as main_views
urlpatterns = [
    path('', main_views.home, name='home'),
    path('register/', main_views.register, name="register"),
    path('addDrive/', main_views.drivePermission, name="add_drive"),
    path('oauth2callback', main_views.auth_return, name="auth_return"),
]
