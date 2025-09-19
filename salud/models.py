from django.db import models

# Create your models here.

class VeterinaryClinic(models.Model):
    name = models.CharField(max_length=30)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    consultPrice = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    services = models.TextField(max_length=200, null=True, blank=True, verbose_name="Servicios")
    description = models.TextField(max_length=200, null=True, blank=True, verbose_name="Descripción")
    photo_url = models.URLField(null=True, blank=True, verbose_name="URL de foto")
    horarioStart = models.TimeField(null=True, blank=True, verbose_name="Horario de apertura")
    horarioEnd = models.TimeField(null=True, blank=True, verbose_name="Horario de cierre")
    specialties = models.TextField(max_length=200, null=True, blank=True, verbose_name="Especialidades")
    valoration = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True, verbose_name="Valoración")
    comments = models.TextField(max_length=1000, null=True, blank=True, verbose_name="Comentarios")

    def __str__(self):
        return self.name