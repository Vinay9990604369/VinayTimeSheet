from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from datetime import timedelta


class Client(models.Model):
    company_name = models.CharField(max_length=255, unique=True)  # Previously 'name'
    client_id = models.CharField(max_length=50, unique=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"{self.company_name} ({self.client_id})"


class Project(models.Model):
    name = models.CharField(max_length=255)  # Project Name
    project_id = models.CharField(max_length=100, unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='projects')
    service_provider = models.CharField(max_length=255)
    service_type = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.project_id})"


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('CONSULTANT', 'Billing Consultant'),
        ('CLIENT', 'Client'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CONSULTANT')

    clients = models.ManyToManyField(
        Client,
        blank=True,
        related_name='client_users',
        help_text="Only applicable for users with the 'Client' role."
    )

    def clean(self):
        if self.role == 'CLIENT' and self.clients.count() == 0:
            raise ValidationError("Client users must be associated with at least one client.")
        if self.role != 'CLIENT' and self.clients.exists():
            raise ValidationError("Only client users can be associated with clients.")

    def __str__(self):
        return self.username


class TimesheetEntry(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='timesheet_entries')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='timesheet_entries')

    phase = models.CharField(
        max_length=50,
        choices=[
            ('Discovery', 'Discovery'),
            ('Prepare', 'Prepare'),
            ('Explore', 'Explore'),
            ('Realise', 'Realise'),
            ('Deploy', 'Deploy'),
            ('Run', 'Run'),
        ]
    )

    billing_consultant = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'CONSULTANT'},
        related_name='timesheet_entries'
    )

    date_of_service = models.DateField()
    billing_time_duration = models.DurationField(
        help_text="Format: HH:MM:SS",
        default=timedelta(0)
    )
    work_description = models.TextField(blank=True)
    comments = models.TextField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.project.name} - {self.billing_consultant.username} - {self.date_of_service}"

    # Computed, read-only fields for convenience in templates
    @property
    def client_name(self):
        return self.client.company_name

    @property
    def client_id(self):
        return self.client.client_id

    @property
    def project_name(self):
        return self.project.name

    @property
    def project_id(self):
        return self.project.project_id

    @property
    def service_provider(self):
        return self.project.service_provider

    @property
    def service_type(self):
        return self.project.service_type

    @property
    def consultant_name(self):
        return self.billing_consultant.get_full_name() or self.billing_consultant.username
