from django.shortcuts import render
from django.contrib.auth.models import User
from .models import *
from django.contrib import messages

def user_list(request):
    users = User.objects.all()
    context = {
        'users': users,
    }
    return render(request, 'user_list.html', context)