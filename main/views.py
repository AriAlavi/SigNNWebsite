from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from main.authorize import authorize

from main.forms import NewProfileForm
from main.models import GoogleCreds, Profile

def home(request):
    return render(request, "main/home.html")

def register(request):
    # if request.user.profile:
    #     return redirect('home')
    form = UserCreationForm(request.POST or None)
    profile_form = NewProfileForm(request.POST or None)
    if form.is_valid() and profile_form.is_valid():
        user = form.save()
        profile = profile_form.save(commit=False)
        profile.user = user
        user.email = profile.email
        user.save()
        profile.save()
        return redirect('home')
    context= {
        'form' : form,
        'register' : profile_form,
    }
    return render(request, "main/register.html", context)

def upload(request):
    return render(request, "main/upload.html")

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from oauth2client.client import flow_from_clientsecrets
from oauth2client.contrib import xsrfutil


SCOPES = ['https://www.googleapis.com/auth/drive.file']

if settings.GOOGLE_SECRETS:
    FLOW = flow_from_clientsecrets(
        settings.GOOGLE_SECRETS,
        scope=SCOPES,
        redirect_uri= settings.HTTP_OR_HTTPS + settings.MAIN_URL + "/oauth2callback",
        prompt='consent')

    def drivePermission(request):
        if not request.user.profile.api_allowed:
            messages.error(request, "You do not have sufficient permissions to add your Google Drive")
        try:
            if request.user.profile.googlecreds.getCreds():
                messages.success(request, "Google creds already in system")
                return redirect('home')
        except Exception:
            pass

        FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY,
                                                request.user)
        url = FLOW.step1_get_authorize_url()
        return HttpResponseRedirect(url)

    def auth_return(request):
        get_state = bytes(request.GET.get('state'), 'utf8')
        if not xsrfutil.validate_token(settings.SECRET_KEY, get_state, request.user):
            return HttpResponseBadRequest()
        
        creds = FLOW.step2_exchange(request.GET.get('code'))
        authorize(creds, ("drive", "v3"))
        cred = GoogleCreds.Initialize(request.user.profile, creds)
        return HttpResponseRedirect("/")
else:
    def drivePermission(request):
        messages.error(request, "Google API is not configued for this medium")
        return redirect('home')
    def auth_return(request):
        messages.error(request, "Google API is not configued for this medium")
        return redirect('home')