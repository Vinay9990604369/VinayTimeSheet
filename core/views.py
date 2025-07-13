from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import TimesheetEntryForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect_dashboard(request)

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect_dashboard(request)
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, 'core/login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


def redirect_dashboard(request):
    """Helper function to redirect user based on role."""
    role = request.user.role
    if role == "ADMIN":
        return redirect('admin_dashboard')
    elif role == "CONSULTANT":
        return redirect('consultant_dashboard')
    elif role == "CLIENT":
        return redirect('client_dashboard')
    else:
        messages.error(request, "User role undefined.")
        return redirect('login')


# Role-based dashboard views
@login_required
def admin_dashboard(request):
    if request.user.role != 'ADMIN':
        messages.error(request, "Access denied: admin only.")
        return redirect('login')
    return render(request, 'core/admin_dashboard.html')


@login_required
def consultant_dashboard(request):
    if request.user.role != 'CONSULTANT':
        messages.error(request, "Access denied: consultant only.")
        return redirect('login')
    return render(request, 'core/consultant_dashboard.html')


@login_required
def client_dashboard(request):
    if request.user.role != 'CLIENT':
        messages.error(request, "Access denied: client only.")
        return redirect('login')
    return render(request, 'core/client_dashboard.html')


@login_required
def timesheet_entry(request):
    if request.method == 'POST':
        form = TimesheetEntryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Timesheet entry saved successfully.")
            return redirect('timesheet_entry')
    else:
        form = TimesheetEntryForm()

    return render(request, 'core/timesheet_entry.html', {'form': form})
