import json
import os
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import TimesheetEntryForm

# Path to credentials.json file for user authentication
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), 'credentials.json')

def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            with open(CREDENTIALS_FILE) as file:
                users = json.load(file)
        except FileNotFoundError:
            messages.error(request, "Credentials file not found.")
            return render(request, 'core/login.html')

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

@login_required
def timesheet_entry(request):
    if request.method == 'POST':
        form = TimesheetEntryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('timesheet_entry')  # redirect to same page after saving
    else:
        form = TimesheetEntryForm()

    return render(request, 'core/timesheet_entry.html', {'form': form})
