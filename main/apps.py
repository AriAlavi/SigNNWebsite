from django.apps import AppConfig
from main.storage import StorageSystemLoop

class MainConfig(AppConfig):
    name = 'main'
    def ready(self):
        StorageSystemLoop()

