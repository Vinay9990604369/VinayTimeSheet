# core/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('CONSULTANT', 'Billing Consultant'),
        ('CLIENT', 'Client'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CONSULTANT')

    def __str__(self):
        return self.username


class TimesheetEntry(models.Model):
    client_name = models.CharField(max_length=255)
    client_id = models.CharField(max_length=100)
    project_name = models.CharField(max_length=255)
    project_id = models.CharField(max_length=100)
    service_provider = models.CharField(max_length=255)
    service_type = models.CharField(max_length=100)

    PHASE_CHOICES = [
        ('Discovery', 'Discovery'),
        ('Prepare', 'Prepare'),
        ('Explore', 'Explore'),
        ('Realise', 'Realise'),
        ('Deploy', 'Deploy'),
        ('Run', 'Run'),
    ]
    phase = models.CharField(max_length=50, choices=PHASE_CHOICES)

    billing_consultant = models.ForeignKey(
        'core.CustomUser',
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'CONSULTANT'},
    )

    date_of_service = models.DateField()
    billing_time = models.TimeField(help_text="Format HH:MM")
    description = models.TextField()
    comments = models.TextField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.project_name} - {self.billing_consultant.username} - {self.date_of_service}"
