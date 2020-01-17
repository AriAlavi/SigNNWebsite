from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

from main.forms import NewProfileForm

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