from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from django.conf import settings
from apiclient.http import MediaFileUpload, MediaIoBaseDownload

from main.lib import build_url

from httplib2 import Http
import os
import uuid
import jsonpickle

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField()
    api_allowed = models.BooleanField(default=False)
    view_allowed = models.BooleanField(default=False)
    uploads_denied = models.PositiveSmallIntegerField(default=0)

    folder = models.CharField(max_length=499, null=True, blank=True)

    def __str__(self):
        return str(self.user)

    def getFolder(self):
        if self.folder:
            return self.folder

        return self.googlecreds.createFolder()
        
    @property
    def unauthorized_file_holder(self):
        if self.api_allowed:
            return False
        if GoogleFile.objects.filter(owned_by=self).count() > 0:
            return True
        return False

    @property
    def ucsb_account(self):
        if self.email.split("@")[-1] == "ucsb.edu":
            return True
        return False

    @property
    def has_creds(self):
        try:
            self.googlecreds
            return True
        except:
            return False


        

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


class TrainingWord(models.Model):
    name = models.CharField(unique=True, max_length=63)
    readonly_fields=('name',)



class DynamicFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True)
    readonly_fields=('id',)
    def getURL(self):
        return self.url
    class Meta:
        abstract = True

class TempLocalFile(DynamicFile):
    name = models.CharField(max_length=99)
    file = models.FileField(upload_to='temp_local/', unique=True)
    uploaded_by = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)


    def getURL(self):
        return build_url(self.file.name)

    @staticmethod
    def Initialize(name, pythonFile, uploader):
        assert isinstance(name, str)
        assert isinstance(uploader, Profile)

        this = TempLocalFile(name=name, uploaded_by=uploader)
        this.file.name = pythonFile
        this.save()
        return this
    
    def __str__(self):
        return self.file.path

    @staticmethod
    def InititalizeForm(givenForm, uploader):
        from main.forms import NewFileForm
        from main.models import GoogleFile
        assert isinstance(givenForm, NewFileForm)
        assert isinstance(uploader, Profile)
        try:
            result = givenForm.save(commit=False)
            result.uploaded_by = uploader
            result.save()
        except Exception as e:
            return "Uploaded file is corrupted. Please try another. Details: {}".format(e)
        return result

@receiver(pre_delete)
def TempFileDeleteSignal(**kwargs):
    instance = kwargs.get("instance", None)
    if not isinstance(instance, TempLocalFile):
        return None
    try:
        os.remove(instance.file.path)
    except Exception as e:
        print("Failed to delete temp local file! Reason:", e)
        

class GoogleFile(DynamicFile):
    owned_by = models.ForeignKey(Profile, null=True, on_delete=models.SET_NULL, related_name="owner") # Owner is the person who's drive is hosting the file
    uploaded_by = models.ForeignKey(Profile, null=True, on_delete=models.SET_NULL, related_name="uploader") # Uploader is the person who contributed the file to the server
    name = models.CharField(max_length=99)
    extension = models.CharField(max_length=7)
    gid = models.CharField(max_length=499)

    approved = models.BooleanField(default=False)
    
    @property
    def url(self):
        # https://drive.google.com/file/d/1HXVYuK8yL9Ve1NBreXcTtCY0dmPEWSFy/view
        return "https://drive.google.com/file/d/" + self.gid + "/view"

    def __str__(self):
        return self.url

    @staticmethod
    def InitializeMedia(file_owner, media, name, extension, uploaded_file ,tag=None):
        assert isinstance(file_owner, Profile)
        assert isinstance(media, MediaFileUpload)
        drive_service = file_owner.googlecreds.getDrive()
        assert drive_service, "Profile has no associated crednetials"
        metadata = {
            'name' : name,
            'uploadType' : "media",
            "parents" : [file_owner.getFolder(),]
        }
        filedata = drive_service.files().create(
            body=metadata, media_body=media, fields='id,webViewLink'
        ).execute()
        permission = {
            'type' : 'anyone',
            'role' : 'reader'
        }
        googlefile = GoogleFile(owned_by=file_owner, gid = filedata['id'], name=name, uploaded_by=uploaded_file)
        drive_service.permissions().create(fileId=filedata['id'], body=permission, fields='').execute()
        googlefile.save()
        return googlefile

    @staticmethod
    def InitializeTempFile(preDrive, owner, tag=None):
        assert isinstance(preDrive, TempLocalFile)
        name = preDrive.name
        path = preDrive.file.path
        extension = os.path.splitext(path)[1]
        assert isinstance(owner, Profile)
        assert os.path.isfile(path)

        media = MediaFileUpload(path)
        drive = GoogleFile.InitializeMedia(owner, media, name, extension, preDrive.uploaded_by, tag)
        drive.save()
        preDrive.delete()
        return drive

    def download_and_delete(self):
        DOWNLOAD_LOCATION = os.path.join(settings.MEDIA_ROOT, "temp_local")
        DOWNLOAD_LOCATION = os.path.join(DOWNLOAD_LOCATION, str(uuid.uuid4()) + self.extension)
        drive_service = self.owned_by.googlecreds.getDrive()
        request = drive_service.files().get_media(fileId=self.gid)
        fh = open(DOWNLOAD_LOCATION, "wb")
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download {}%".format(int(status.progress() * 100)))

        fh.close()
        local = TempLocalFile(name=self.name, file=DOWNLOAD_LOCATION, uploaded_by=self.uploaded_by)
        self.delete()
        return local



    def delete_google(self):
        drive_service = self.owned_by.googlecreds.getDrive()
        drive_service.files().delete(fileId=self.gid).execute()

@receiver(pre_delete)
def GoogleFileDeleteSignal(**kwargs):
    instance = kwargs.get("instance", None)
    if not(instance) or not(isinstance(instance, GoogleFile)):
        return None
    try:
        instance.delete_google()
    except Exception as e:
        print("Failed to delete temp local file! Reason:", e)
        