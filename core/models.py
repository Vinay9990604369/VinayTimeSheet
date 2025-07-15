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

    class Meta:
        ordering = ['company_name']
        verbose_name = "Client"
        verbose_name_plural = "Clients"


class Project(models.Model):
    name = models.CharField(max_length=255)  # Project Name
    project_id = models.CharField(max_length=100, unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='projects')
    service_provider = models.CharField(max_length=255)
    service_type = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.project_id})"

    class Meta:
        ordering = ['name']
        verbose_name = "Project"
        verbose_name_plural = "Projects"


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
        super().clean()
        # Validate client association only if the instance is saved or has a pk
        if self.role == 'CLIENT':
            if not self.pk and not self.clients.exists():
                raise ValidationError("Client users must be associated with at least one client.")
            elif self.pk and self.clients.count() == 0:
                raise ValidationError("Client users must be associated with at least one client.")
        else:
            if self.clients.exists():
                raise ValidationError("Only client users can be associated with clients.")

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


class TimesheetEntry(models.Model):
    PHASE_CHOICES = [
        ('Discovery', 'Discovery'),
        ('Prepare', 'Prepare'),
        ('Explore', 'Explore'),
        ('Realise', 'Realise'),
        ('Deploy', 'Deploy'),
        ('Run', 'Run'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='timesheet_entries')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='timesheet_entries')

    phase = models.CharField(max_length=50, choices=PHASE_CHOICES)

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

    # Convenience properties for template use
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

    @property
    def billing_hours(self):
        """Return billing_time_duration as float hours."""
        if self.billing_time_duration:
            return self.billing_time_duration.total_seconds() / 3600
        return 0.0

    class Meta:
        ordering = ['-date_of_service', 'billing_consultant']
        verbose_name = "Timesheet Entry"
        verbose_name_plural = "Timesheet Entries"
        unique_together = ('billing_consultant', 'project', 'date_of_service')  # optional constraint
