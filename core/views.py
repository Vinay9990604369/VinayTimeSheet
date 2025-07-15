from calendar import monthrange
from datetime import date, datetime, timedelta
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden

from .models import Client, Project, TimesheetEntry


@login_required
def redirect_after_login(request):
    """Redirect user based on their role after login."""
    if request.user.role == 'ADMIN':
        return redirect('core:admin_dashboard')
    elif request.user.role == 'CONSULTANT':
        return redirect('core:consultant_dashboard')
    elif request.user.role == 'CLIENT':
        return redirect('core:client_dashboard')
    else:
        messages.error(request, "Invalid user role.")
        return redirect('core:login')


@login_required
def timesheet_entry(request):
    """Consultant view to add/update timesheet entries for a selected client, project, and month."""
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
            # Restrict projects dropdown to selected client
            projects = Project.objects.filter(client_id=selected_client_id)
            num_days = monthrange(year, month)[1]

            # Fetch existing entries for the selected month
            existing_entries = TimesheetEntry.objects.filter(
                billing_consultant=request.user,
                client_id=selected_client_id,
                project_id=selected_project_id,
                date_of_service__year=year,
                date_of_service__month=month,
            ).select_related('client', 'project')

            existing_dates = set(entry.date_of_service for entry in existing_entries)

            # Create missing TimesheetEntry records
            with transaction.atomic():
                for day in range(1, num_days + 1):
                    day_date = date(year, month, day)
                    if day_date not in existing_dates:
                        TimesheetEntry.objects.create(
                            billing_consultant=request.user,
                            client_id=selected_client_id,
                            project_id=selected_project_id,
                            date_of_service=day_date,
                            phase='Discovery',
                        )

            # Reload entries
            timesheet_entries = TimesheetEntry.objects.filter(
                billing_consultant=request.user,
                client_id=selected_client_id,
                project_id=selected_project_id,
                date_of_service__year=year,
                date_of_service__month=month,
            ).select_related('client', 'project').order_by('date_of_service')

            # Add duration_in_hours property for each entry
            for entry in timesheet_entries:
                entry.duration_in_hours = (
                    entry.billing_time_duration.total_seconds() / 3600
                    if entry.billing_time_duration
                    else 0
                )

            if request.method == 'POST':
                any_error = False
                for entry in timesheet_entries:
                    duration_key = f'duration_{entry.id}'
                    description_key = f'description_{entry.id}'
                    remarks_key = f'remarks_{entry.id}'
                    phase_key = f'phase_{entry.id}'

                    duration_val = request.POST.get(duration_key)
                    description_val = request.POST.get(description_key)
                    remarks_val = request.POST.get(remarks_key)
                    phase_val = request.POST.get(phase_key)

                    try:
                        duration_float = float(duration_val) if duration_val else 0
                        if duration_float < 0 or duration_float > 24:
                            raise ValueError("Invalid duration")
                    except Exception:
                        messages.error(request, f"Invalid billing time duration for {entry.date_of_service}.")
                        any_error = True
                        continue

                    valid_phases = dict(TimesheetEntry._meta.get_field('phase').choices).keys()
                    if phase_val not in valid_phases:
                        messages.error(request, f"Invalid phase for {entry.date_of_service}.")
                        any_error = True
                        continue

                    entry.billing_time_duration = timedelta(hours=duration_float)
                    entry.work_description = description_val
                    entry.comments = remarks_val
                    entry.phase = phase_val
                    entry.save()

                if not any_error:
                    messages.success(request, "Timesheet entries updated successfully.")
                    url = f"{request.path}?client={selected_client_id}&project={selected_project_id}&month={selected_month}"
                    return redirect(url)

    context = {
        'clients': clients,
        'projects': projects,
        'timesheet_entries': timesheet_entries,
        'selected_client_id': selected_client_id,
        'selected_project_id': selected_project_id,
        'selected_month': selected_month,
        'phase_choices': TimesheetEntry._meta.get_field('phase').choices,
    }

    return render(request, 'core/timesheet_entry.html', context)


@login_required
def admin_dashboard(request):
    """Render admin dashboard."""
    return render(request, 'core/admin_dashboard.html')


@login_required
def consultant_dashboard(request):
    """Consultant dashboard with filtering on client, project, and month."""
    selected_client_id = request.GET.get('client')
    selected_project_id = request.GET.get('project')
    selected_month = request.GET.get('month')

    try:
        selected_client_id = int(selected_client_id) if selected_client_id else None
    except ValueError:
        selected_client_id = None

    try:
        selected_project_id = int(selected_project_id) if selected_project_id else None
    except ValueError:
        selected_project_id = None

    clients = Client.objects.all()
    projects = Project.objects.all()

    timesheet_entries = TimesheetEntry.objects.all()
    if selected_client_id:
        timesheet_entries = timesheet_entries.filter(client_id=selected_client_id)
        projects = projects.filter(client_id=selected_client_id)
    if selected_project_id:
        timesheet_entries = timesheet_entries.filter(project_id=selected_project_id)
    if selected_month:
        try:
            selected_date = datetime.strptime(selected_month, "%Y-%m")
            timesheet_entries = timesheet_entries.filter(
                date_of_service__year=selected_date.year,
                date_of_service__month=selected_date.month
            )
        except ValueError:
            pass

    timesheet_entries = timesheet_entries.select_related('client', 'project', 'billing_consultant').order_by('date_of_service')

    context = {
        'clients': clients,
        'projects': projects,
        'timesheet_entries': timesheet_entries,
        'selected_client_id': selected_client_id,
        'selected_project_id': selected_project_id,
        'selected_month': selected_month,
    }
    return render(request, 'core/consultant_dashboard.html', context)


@login_required
def client_dashboard(request):
    """Render client dashboard."""
    return render(request, 'core/client_dashboard.html')


@login_required
def timesheet_entry_edit(request, entry_id):
    """Allow consultants to edit a single timesheet entry."""
    entry = get_object_or_404(TimesheetEntry, id=entry_id)

    if request.user.role != 'CONSULTANT' or entry.billing_consultant != request.user:
        return HttpResponseForbidden("You do not have permission to edit this entry.")

    if request.method == 'POST':
        duration = request.POST.get('duration')
        description = request.POST.get('description')
        remarks = request.POST.get('remarks')
        phase = request.POST.get('phase')

        try:
            duration_float = float(duration)
            if not 0 <= duration_float <= 24:
                raise ValueError("Invalid duration")
        except Exception:
            messages.error(request, "Invalid duration.")
        else:
            entry.billing_time_duration = timedelta(hours=duration_float)
            entry.work_description = description
            entry.comments = remarks
            entry.phase = phase
            entry.save()
            messages.success(request, "Entry updated successfully.")
            return redirect('core:consultant_dashboard')

    context = {
        'entry': entry,
        'phase_choices': TimesheetEntry._meta.get_field('phase').choices,
    }
    return render(request, 'core/timesheet_entry_edit.html', context)
