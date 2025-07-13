from django.db import models
from django.contrib.auth.models import AbstractUser

class Client(models.Model):
    company_name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.company_name

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('CONSULTANT', 'Billing Consultant'),
        ('CLIENT', 'Client'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CONSULTANT')

    # Many-to-many link to clients ONLY meaningful if role=CLIENT
    clients = models.ManyToManyField(Client, blank=True, related_name='users')

    def __str__(self):
        return self.username
