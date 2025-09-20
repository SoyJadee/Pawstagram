from django.db import models

# Create your models here.
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

# Create your models here.

class ServicesHealth(models.Model):
    name = models.CharField(max_length=30)
    type = models.CharField(max_length=30, choices=[('veterinaria', 'Veterinaria'), ('peluqueria', 'Peluquería'), ('spa', 'Spa')])
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    consultPrice = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    owner = models.CharField(max_length=40, verbose_name="Dueño del servicio",default=None)
    services = models.TextField(max_length=200, null=True, blank=True, verbose_name="Servicios")
    description = models.TextField(max_length=200, null=True, blank=True, verbose_name="Descripción")
    photo_url = models.URLField(null=True, blank=True, verbose_name="URL de foto")
    horarioStart = models.TimeField(null=True, blank=True, verbose_name="Horario de apertura")
    horarioEnd = models.TimeField(null=True, blank=True, verbose_name="Horario de cierre")
    specialties = models.TextField(max_length=200, null=True, blank=True, verbose_name="Especialidades")
    valoration = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True, editable=False, verbose_name="Valoración")
    comments = models.TextField(max_length=1000, null=True, blank=True, editable=False, verbose_name="Comentarios")
    coordinates = models.CharField(max_length=100, null=True, blank=True, verbose_name="Coordenadas")

    def __str__(self):
        return self.name