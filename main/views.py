from django.shortcuts import render, redirect, HttpResponseRedirect, Http404
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from main.authorize import authorize

from main.forms import NewProfileForm, NewFileForm
from main.models import GoogleCreds, Profile, TempLocalFile, GoogleFile, TempLocalFile

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from oauth2client.client import flow_from_clientsecrets
from oauth2client.contrib import xsrfutil

def profiles(request):
    if not request.user.profile.verify_allowed:
        return redirect("profile")
    
    profile_stats = []
    for profile in Profile.objects.all():
        stats = profile.upload_stats
        stats["profile"] = profile
        profile_stats.append(stats)

    context = {
        "stats" : profile_stats
    }


    return render(request, "main/profiles.html", context)


def profile(request):
    profile = request.user.profile
    context = profile.upload_stats
    context['profile'] = profile

    return render(request, "main/profile.html", context)

def home(request):
    if request.POST:
        form = NewFileForm(request.POST, request.FILES)
        if form.is_valid():
            e = TempLocalFile.InititalizeForm(form, request.user.profile)
            print("RESULT:", e)
            messages.success(request, "File uploaded")
            return redirect("home")
    else:
        form = NewFileForm()

    context = {
        'test_form' : form
    }
    return render(request, "main/home.html", context)

def view_image(request, id):
    if not request.user.profile.view_allowed:
        return redirect("profile")
    try:
        image = GoogleFile.objects.get(id=id)
    except:
        try:
            image = TempLocalFile.objects.get(id=id)
        except:
            return Http404()
    return redirect(image.getURL())

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
        if "@ucsb.edu" in profile.email:
            profile.view_allowed = True
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







if settings.GOOGLE_SECRETS:
    SCOPES = ('https://www.googleapis.com/auth/drive.file',)
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

    def add_drive_terms(request):
        return render(request, "main/add_drive_confirm.html")

    def auth_return(request):
        get_state = bytes(request.GET.get('state'), 'utf8')
        if not xsrfutil.validate_token(settings.SECRET_KEY, get_state, request.user):
            return HttpResponseBadRequest()
        
        creds = FLOW.step2_exchange(request.GET.get('code'))
        authorize(creds, ("drive", "v3"))
        cred = GoogleCreds.Initialize(request.user.profile, creds)
        messages.success(request, "Your Google Drive has been added to our storage pool")
        return HttpResponseRedirect("/")
else:
    def drivePermission(request):
        messages.error(request, "Google API is not configued for this medium:\n" + settings.GOOGLE_SECRETS_BROKEN_WHY)
        return redirect('home')
    def auth_return(request):
        messages.error(request, "Google API is not configued for this medium:\n" + settings.GOOGLE_SECRETS_BROKEN_WHY)
        return redirect('home')
    def add_drive_terms(request):
        messages.error(request, "Google API is not configued for this medium:\n" + settings.GOOGLE_SECRETS_BROKEN_WHY)
        return redirect('home')