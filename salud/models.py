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
    coordinates = models.CharField(max_length=100, null=True, blank=True, verbose_name="Coordenadas")

    def __str__(self):
        return self.name
    
class Reviews(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID de reseña")
    service = models.ForeignKey(ServicesHealth, on_delete=models.CASCADE, related_name='reviews', verbose_name="Servicio de salud")
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Valoración",
        default=Decimal('0.0'),
        blank=False,
        null=False
    )
    comment = models.TextField(max_length=500, verbose_name="Comentario")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    email = models.EmailField(verbose_name="Correo electrónico",null=False, blank=False,default="")

    def __str__(self):
        return f"Reseña de {self.email} para {self.service.name}"

