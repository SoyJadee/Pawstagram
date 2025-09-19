from django.db import models
from usuarios.models import UserProfile
class Pet(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID de mascota")
    creator = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='created_pets',
        verbose_name="ID de la persona que publica",
        default=None
    )
    owner = models.ForeignKey(
        UserProfile,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='owned_pets'
    )
    age = models.IntegerField(null=True, blank=True,verbose_name="Edad")
    breed = models.CharField(max_length=50,verbose_name="Raza",default="Meztizo")
    gender = models.CharField(max_length=10, choices=[
        ('male', 'Macho'),
        ('female', 'Hembra'),
        ('unknown', 'Desconocido')
    ], default='unknown', verbose_name="Género")
    name = models.CharField(max_length=20,verbose_name="Nombre")
    description = models.TextField(null=True, blank=True,verbose_name="Descripción")
    profile_photo_url = models.TextField(null=True, blank=True,verbose_name="URL de foto de perfil")
    is_available_for_adoption = models.BooleanField(default=False,verbose_name="Disponible para adopción")
    ubication = models.CharField(max_length=100, null=True, blank=True,verbose_name="Ubicación")
    created_at = models.DateTimeField(auto_now_add=True,verbose_name="Fecha de creación")
    vacunas = models.BooleanField(default=False,verbose_name="Vacunas")