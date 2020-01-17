from django.forms import ModelForm
from main.models import Profile

class NewProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ("email",)