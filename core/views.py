from calendar import monthrange
from datetime import date, datetime, timedelta
from django.db import transaction

@login_required
def timesheet_entry(request):
    if request.user.role != 'CONSULTANT':
        messages.error(request, "Access denied.")
        return redirect('login')

    clients = Client.objects.all()
    projects = Project.objects.all()

    selected_client_id = request.GET.get('client')
    selected_project_id = request.GET.get('project')
    selected_month = request.GET.get('month')

    timesheet_entries = []

    if selected_client_id and selected_project_id and selected_month:
        # Validate selected month format and parse year/month
        try:
            selected_date = datetime.strptime(selected_month, "%Y-%m")
            year = selected_date.year
            month = selected_date.month
        except ValueError:
            messages.error(request, "Invalid month format. Use YYYY-MM.")
            year = None
            month = None

        if year and month:
            # Filter projects by client for dropdown accuracy
            projects = Project.objects.filter(client_id=selected_client_id)

            # Get or create timesheet entries for every day in the month
            num_days = monthrange(year, month)[1]
            first_day = date(year, month, 1)

            # Bulk create missing entries
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
                        # Create new TimesheetEntry with autopopulated data
                        TimesheetEntry.objects.create(
                            billing_consultant=request.user,
                            client_id=selected_client_id,
                            project_id=selected_project_id,
                            date_of_service=day_date,
                            # For these fields, you can customize the defaults or leave blank
                            service_provider="Auto-filled or default",
                            service_type="Auto-filled or default",
                            phase="Auto-filled or default",
                            last_updated=datetime.now(),
                        )

            # Refresh the entries queryset after creation
            timesheet_entries = TimesheetEntry.objects.filter(
                billing_consultant=request.user,
                client_id=selected_client_id,
                project_id=selected_project_id,
                date_of_service__year=year,
                date_of_service__month=month,
            ).select_related('client', 'project').order_by('date_of_service')

            # Handle POST to save edited fields
            if request.method == 'POST':
                any_error = False
                for entry in timesheet_entries:
                    # Extract POSTed data for each entry by its ID
                    duration_key = f'duration_{entry.id}'
                    description_key = f'description_{entry.id}'
                    remarks_key = f'remarks_{entry.id}'

                    duration_val = request.POST.get(duration_key)
                    description_val = request.POST.get(description_key)
                    remarks_val = request.POST.get(remarks_key)

                    # Validate duration (optional: can add more checks)
                    try:
                        duration_float = float(duration_val) if duration_val else 0
                        if duration_float < 0 or duration_float > 24:
                            raise ValueError("Invalid duration")
                    except Exception:
                        messages.error(request, f"Invalid billing time duration for date {entry.date_of_service}.")
                        any_error = True
                        continue

                    # Update the entry fields
                    entry.duration = duration_float
                    entry.description = description_val
                    entry.remarks = remarks_val
                    entry.last_updated = datetime.now()
                    entry.save()

                if not any_error:
                    messages.success(request, "Timesheet entries updated successfully.")
                    # Redirect to GET after POST to avoid resubmission
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
