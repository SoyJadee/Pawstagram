from django.db import models
from mascota.models import Pet
from usuarios.models import UserProfile


class Adoption(models.Model):
    pet = models.ForeignKey(
        Pet,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='adoptions',
        verbose_name='Mascota'
    )
    adopterName = models.CharField(
        max_length=40, null=True, blank=True, verbose_name='Nombre del adoptante')
    adopterEmail = models.EmailField(
        max_length=100, null=True, blank=True, verbose_name='Email del adoptante')
    adopterPhone = models.CharField(
        max_length=20, null=True, blank=True, verbose_name='Teléfono del adoptante')
    message = models.TextField(
        max_length=150, null=True, blank=True, verbose_name='Mensaje')
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Fecha de creación')
    is_read = models.BooleanField(
        default=False, verbose_name='Leído por responsable')

    class Meta:
        verbose_name = 'Adopción'
        verbose_name_plural = 'Adopciones'

    def __str__(self):
        return f"Adopción de {self.pet.name} por {self.adopterName if self.adopterName else 'Desconocido'}"
