from django.forms import ModelForm
from main.models import Profile, TempLocalFile

class NewProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ("email",)

class NewFileForm(ModelForm):
    class Meta:
        model = TempLocalFile
        fields = ("name", "file")