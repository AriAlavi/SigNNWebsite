import os

from django.apps import AppConfig
from main.storage import StorageSystemLoop

class MainConfig(AppConfig):
    name = 'main'
    def ready(self):
        if os.environ.get("RUN_MAIN") == "true":
            StorageSystemLoop()

