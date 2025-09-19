from django.db import models
from mascota.models import Pet
from usuarios.models import UserProfile

class Adoption(models.Model):
    STATUS_CHOICES = [
        ('available', 'Disponible'),
        ('pending', 'Pendiente'),
        ('adopted', 'Adoptado'),
    ]

    id = models.AutoField(primary_key=True, verbose_name="ID de adopción")
    pet = models.ForeignKey(
        Pet,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='adoptions',
        verbose_name='Mascota'
    )
    adopter = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='adoptions',
        verbose_name='Adoptante'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, null=True, blank=True, verbose_name='Estado')
    message = models.TextField(null=True, blank=True, verbose_name='Mensaje')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')

    class Meta:
        verbose_name = 'Adopción'
        verbose_name_plural = 'Adopciones'

    def __str__(self):
        pet_name = getattr(self.pet, 'name', None) or 'Mascota'
        adopter_name = getattr(getattr(self.adopter, 'user', None), 'username', None) or 'Usuario'
        return f"Adopción de {pet_name} por {adopter_name}"