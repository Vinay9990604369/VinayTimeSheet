from calendar import monthrange
from datetime import date, datetime, timedelta
from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Client, Project, TimesheetEntry


@login_required
def timesheet_entry(request):
    if request.user.role != 'CONSULTANT':
        messages.error(request, "Access denied.")
        return redirect('core:login')

    clients = Client.objects.all()
    projects = Project.objects.all()

    selected_client_id = request.GET.get('client')
    selected_project_id = request.GET.get('project')
    selected_month = request.GET.get('month')

    timesheet_entries = []

    if selected_client_id and selected_project_id and selected_month:
        try:
            selected_date = datetime.strptime(selected_month, "%Y-%m")
            year = selected_date.year
            month = selected_date.month
        except ValueError:
            messages.error(request, "Invalid month format. Use YYYY-MM.")
            year = None
            month = None

        if year and month:
            projects = Project.objects.filter(client_id=selected_client_id)

            num_days = monthrange(year, month)[1]
            first_day = date(year, month, 1)

            existing_entries = TimesheetEntry.objects.filter(
                billing_consultant=request.user,
                client_id=selected_client_id,
                project_id=selected_project_id,
                date_of_service__year=year,
                date_of_service__month=month,
            ).select_related('client', 'project')

            existing_dates = set(entry.date_of_service for entry in existing_entries)

            with transaction.atomic():
                for day in range(1, num_days + 1):
                    day_date = date(year, month, day)
                    if day_date not in existing_dates:
                        TimesheetEntry.objects.create(
                            billing_consultant=request.user,
                            client_id=selected_client_id,
                            project_id=selected_project_id,
                            date_of_service=day_date,
                        )

            timesheet_entries = TimesheetEntry.objects.filter(
                billing_consultant=request.user,
                client_id=selected_client_id,
                project_id=selected_project_id,
                date_of_service__year=year,
                date_of_service__month=month,
            ).select_related('client', 'project').order_by('date_of_service')

            if request.method == 'POST':
                any_error = False
                for entry in timesheet_entries:
                    duration_key = f'duration_{entry.id}'
                    description_key = f'description_{entry.id}'
                    remarks_key = f'remarks_{entry.id}'

                    duration_val = request.POST.get(duration_key)
                    description_val = request.POST.get(description_key)
                    remarks_val = request.POST.get(remarks_key)

                    try:
                        duration_float = float(duration_val) if duration_val else 0
                        if duration_float < 0 or duration_float > 24:
                            raise ValueError("Invalid duration")
                    except Exception:
                        messages.error(request, f"Invalid billing time duration for date {entry.date_of_service}.")
                        any_error = True
                        continue

                    entry.billing_time_duration = timedelta(hours=duration_float)
                    entry.work_description = description_val
                    entry.comments = remarks_val
                    entry.save()

                if not any_error:
                    messages.success(request, "Timesheet entries updated successfully.")
                    url = f"{request.path}?client={selected_client_id}&project={selected_project_id}&month={selected_month}"
                    return redirect(url)
    else:
        timesheet_entries = []

    context = {
        'clients': clients,
        'projects': projects,
        'timesheet_entries': timesheet_entries,
        'selected_client_id': selected_client_id,
        'selected_project_id': selected_project_id,
        'selected_month': selected_month,
    }

    return render(request, 'core/timesheet_entry.html', context)


@login_required
def admin_dashboard(request):
    context = {}
    return render(request, 'core/admin_dashboard.html', context)


@login_required
def consultant_dashboard(request):
    context = {}
    return render(request, 'core/consultant_dashboard.html', context)


@login_required
def client_dashboard(request):
    context = {}
    return render(request, 'core/client_dashboard.html', context)
