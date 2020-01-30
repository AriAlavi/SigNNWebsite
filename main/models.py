from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from apiclient.http import MediaFileUpload

from httplib2 import Http
import os
import jsonpickle

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField()
    api_allowed = models.BooleanField(default=False)
    folder = models.CharField(max_length=499, null=True, blank=True)
    def __str__(self):
        return str(self.user)

    def getFolder(self):
        if self.folder:
            return self.folder

        return self.googlecreds.createFolder()
        

        

class GoogleCreds(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, primary_key = True)
    creds  = models.TextField(max_length=2000)

    class NoCredsError(Exception):
        def __init__(self, message, errors):
            super().__init__(message)
            self.errors = errors

    def setCreds(self, creds):
        self.creds = jsonpickle.encode(creds)
        self.save()
        return self

    def getCreds(self):
        if not self.creds:
            raise GoogleCreds.NoCredsError()
        creds = jsonpickle.decode(self.creds)
        if(creds.access_token_expired):
            try:
                creds.refresh(Http())
            except:
                # The credentials were revoked
                self.delete()
                raise GoogleCreds.NoCredsError() 
            self.setCreds(creds)

        return creds

    def getDrive(self):
        from main.authorize import authorize
        return authorize(self.getCreds(), ("drive", "v3"))['drive']

    def createFolder(self):
        from main.authorize import authorize
        FOLDER_NAME = "SIGNN_DATABASE"

        drive_service = self.getDrive()
        file_metadata = {
            'name' : FOLDER_NAME,
            'mimeType' : 'application/vnd.google-apps.folder'
        }
        folder = drive_service.files().create(body=file_metadata,
                                    fields='id').execute()['id']
        self.profile.folder = folder
        self.profile.save()
        return folder

    @staticmethod
    def Initialize(profile, creds):
        assert isinstance(profile, Profile)
        assert profile.api_allowed
        return GoogleCreds(profile=profile).setCreds(creds)

    def __str__(self):
        return str(self.profile)


class TempLocalFile(models.Model):
    name = models.CharField(max_length=99)
    file = models.FileField(upload_to='temp_local/', unique=True)
    uploaded_by = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)

    @staticmethod
    def Initialize(name, pythonFile, uploader):
        assert isinstance(name, str)
        assert isinstance(uploader, Profile)

        this = TempLocalFile(name=name, uploaded_by=uploader)
        this.file.name = pythonFile
        this.save()


        image = DriveImage.InitializeWithPreDrive(this, relatedObject)
        this.delete()
        return image
    
    def __str__(self):
        return self.file.path

    @staticmethod
    def InititalizeForm(givenForm):
        from main.forms import NewFileForm
        from main.models import GoogleFile
        assert isinstance(givenForm, NewFileForm)
        try:
            result = givenForm.save()
        except Exception as e:
            return "Uploaded file is corrupted. Please try another. Details: {}".format(e)
        file = GoogleFile.InitializeTempFile(result, givenForm.name, givenForm.profile)
        result.delete()
        return file

@receiver(pre_delete)
def TempFileDeleteSignal(**kwargs):
    instance = kwargs.get("instance", None)
    if not(instance) or not(isinstance(instance, TempLocalFile)):
        return None
    try:
        os.remove(instance.file.path)
    except Exception as e:
        print("Failed to delete temp local file! Reason:", e)
        

class GoogleFile(models.Model):
    owned_by = models.ForeignKey(Profile, null=True, on_delete=models.SET_NULL)
    gid = models.CharField(max_length=499)
    url = models.URLField()
    
    def __str__(self):
        return self.url

    @staticmethod
    def InitializeMedia(owner, media, tag=None):
        assert isinstance(owner, Profile)
        assert isinstance(media, MediaFileUpload)
        drive_service = self.owned_by.googlecreds.getDrive()
        assert drive_service, "Profile has no associated crednetials"
        metadata = {
            'name' : name,
            'uploadType' : "media",
            "parents" : [owner.getFolder(),]
        }
        filedata = drive_service.files().create(
            body=metadata, media_body=media, fields='id,webViewLink'
        ).execute()
        googlefile = GoogleFile(owned_by=owner, gid = filedata['id'], url='webViewLink')
        googlefile.save()
        return googlefile

    @staticmethod
    def InitializeTempFile(preDrive, tag, uploader):
        assert isinstance(preDrive, TempLocalFile)
        name = preDrive.name
        path = preDrive.file.path
        extension = os.path.splitext(path)[1]
        assert isinstance(uploader, Profile)
        assert os.path.isfile(path)
        assert isinstance(name, str)

        media = MediaFileUpload(path)
        drive = DriveImage.InitializeMedia(uploader, media, tag)
        drive.save()
        preDrive.delete()
        return drive

    def delete(self):
        drive_service = self.owned_by.googlecreds.getDrive()
        drive_service.files().delete(fileId=self.gid).execute()
        super().delete(self)