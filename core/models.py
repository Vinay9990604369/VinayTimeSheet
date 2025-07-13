from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError


class Client(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Client
    client_id = models.CharField(max_length=50, unique=True)  # Client_ID
    address = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.client_id})"


class Project(models.Model):
    name = models.CharField(max_length=255)  # Project
    project_id = models.CharField(max_length=100, unique=True)  # Project_ID
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='projects')
    service_provider = models.CharField(max_length=255)  # Service_Provider
    service_type = models.CharField(max_length=100)  # Service_Type

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
        help_text="Select one or more clients this user belongs to (only for Client users)."
    )

    def clean(self):
        if self.role == 'CLIENT' and self.clients.count() == 0:
            raise ValidationError("Client users must be associated with at least one client.")
        if self.role != 'CLIENT' and self.clients.exists():
            raise ValidationError("Only client users can be associated with clients.")

    def __str__(self):
        return self.username


class TimesheetEntry(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='timesheet_entries')  # Client
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='timesheet_entries')  # Project

    phase = models.CharField(  # Phase
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

    billing_consultant = models.ForeignKey(  # Billing_Consultant
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'CONSULTANT'},
        related_name='timesheet_entries'
    )

    date_of_service = models.DateField()  # Date_of_Service
    billing_time_duration = models.DurationField(help_text="Format: HH:MM:SS")  # Billing_Time_Duration

    work_description = models.TextField()  # Work_Description
    comments = models.TextField(blank=True, null=True)  # Comments

    last_updated = models.DateTimeField(auto_now=True)  # Last_Updated

    def __str__(self):
        return f"{self.project.name} - {self.billing_consultant.username} - {self.date_of_service}"

    # Properties to access read-only fields from related models
    @property
    def client_id(self):
        return self.client.client_id

    @property
    def project_id(self):
        return self.project.project_id

    @property
    def project_name(self):
        return self.project.name

    @property
    def service_type(self):
        return self.project.service_type

    @property
    def service_provider(self):
        return self.project.service_provider
