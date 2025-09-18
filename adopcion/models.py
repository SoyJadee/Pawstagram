from django.db import models
from mascota.models import Pet
from usuarios.models import User


class Adoption(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    id = models.AutoField(primary_key=True, verbose_name="ID de adopción")
    pet = models.ForeignKey(Pet, on_delete=models.SET_NULL, null=True)
    adopter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, null=True)
    message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
