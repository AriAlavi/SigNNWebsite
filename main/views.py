from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

def home(request):
    return render(request, "main/home.html")

def register(request):
    # if request.user.profile:
    #     return redirect('home')
    form = UserCreationForm(request.POST or None)
    context= {
        'form' : form
    }
    return render(request, "main/register.html", context)