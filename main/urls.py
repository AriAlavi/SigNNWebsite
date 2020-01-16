from django.urls import path, include
import main.views as main_views
urlpatterns = [
    path('', main_views.home, name='home')
]
