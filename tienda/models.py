
from django.db import models

class Store(models.Model):
    id = models.AutoField(primary_key=True,verbose_name="Nro de tienda")
    name = models.CharField(max_length=255, verbose_name="Nombre de la tienda")
    description = models.TextField(null=True, blank=True, verbose_name="Descripción")
    # Para 'location', se recomienda usar django.contrib.gis.db.models.PointField si usas GeoDjango
    # Aquí se deja como CharField para coordenadas WKT o similar, pero puedes ajustarlo según tu configuración GIS
    location = models.CharField(max_length=255, null=True, blank=True, verbose_name="Ubicación")
    photo_url = models.URLField(null=True, blank=True, verbose_name="URL de foto")
    created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Fecha de creación")

    def __str__(self):
        return self.name or str(self.id)