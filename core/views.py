from django.shortcuts import render, redirect
import json
import os
from django.contrib import messages
from django.contrib.auth import logout as auth_logout

CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), 'credentials.json')

def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        with open(CREDENTIALS_FILE) as file:
            users = json.load(file)

        user = next((u for u in users if u["email"] == email and u["password"] == password), None)

        if user:
            request.session['user_email'] = user["email"]
            request.session['user_role'] = user["role"]

            if user["role"] == "ADMIN":
                return redirect('admin_dashboard')
            elif user["role"] == "CONSULTANT":
                return redirect('consultant_dashboard')
            elif user["role"] == "CLIENT":
                return redirect('client_dashboard')
        else:
            messages.error(request, "Invalid credentials.")

    return render(request, 'core/login.html')

def logout_view(request):
    auth_logout(request)
    return redirect('login')

def admin_dashboard(request):
    if request.session.get('user_role') != 'ADMIN':
        return redirect('login')
    return render(request, 'core/admin_dashboard.html')

def consultant_dashboard(request):
    if request.session.get('user_role') != 'CONSULTANT':
        return redirect('login')
    return render(request, 'core/consultant_dashboard.html')

def client_dashboard(request):
    if request.session.get('user_role') != 'CLIENT':
        return redirect('login')
    return render(request, 'core/client_dashboard.html')
