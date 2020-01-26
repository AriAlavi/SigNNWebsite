from django.db import models
from django.contrib.auth.models import User

from httplib2 import Http
import jsonpickle

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField()
    api_allowed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)

class GoogleCreds(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, primary_key = True)
    creds  = models.TextField(max_length=2000)

    def setCreds(self, creds):
        self.creds = jsonpickle.encode(creds)
        self.save()
        return self
    def getCreds(self):
        creds = jsonpickle.decode(self.creds)
        if(creds.access_token_expired):
            try:
                creds.refresh(Http())
            except:
                # The credentials were revoked
                self.delete()
                return None
            self.setCreds(creds)

        return creds

    @staticmethod
    def Initialize(profile, creds):
        assert isinstance(profile, Profile)
        assert profile.api_allowed
        return GoogleCreds(profile=profile).setCreds(creds)

    def __str__(self):
        return str(self.profile)