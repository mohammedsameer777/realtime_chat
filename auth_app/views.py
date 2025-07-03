from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect("/chat/test-requests/")
    return render(request, "auth_app/register.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("/chat/test-requests/")
        else:
            messages.error(request, "Invalid credentials")
    return render(request, "auth_app/login.html")

def logout_view(request):
    logout(request)
    return redirect("/login/")
