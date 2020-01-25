from django.db import models
from django.contrib.auth.models import User

from httplib2 import Http
import jsonpickle

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField()
    api_allowed = models.BooleanField(default=False)

# class GoogleCreds(models.Model):
#     profile = models.OneToOneField(Profile, on_delete=models.CASCADE, primary_key = True)
#     creds  = models.TextField(max_length=2000)

#     def setCreds(self, creds):
#         self.creds = jsonpickle.encode(creds)
#     def getCreds(self):
#         creds = jsonpickle.decode(self.creds)
#         if(creds.access_token_expired):
#             try:
#                 creds.refresh(Http())
#             except:
#                 # The credentials were revoked
#                 self.delete()
#                 return None
#             self.setCreds(creds)

#         return creds