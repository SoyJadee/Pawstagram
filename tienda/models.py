from django.core.validators import MinValueValidator
from django.db import models
from decimal import Decimal

class Store(models.Model):
    id = models.AutoField(primary_key=True,verbose_name="Nro de tienda")
    name = models.CharField(max_length=255, verbose_name="Nombre de la tienda")
    description = models.TextField(null=True, blank=True, verbose_name="Descripción")
    owner = models.CharField(max_length=40, verbose_name="Dueño de la tienda",default=None)  # Cambiado a CharField para simplificar
    # Para 'location', se recomienda usar django.contrib.gis.db.models.PointField si usas GeoDjango
    # Aquí se deja como CharField para coordenadas WKT o similar, pero puedes ajustarlo según tu configuración GIS
    location = models.CharField(max_length=255, null=True, blank=True, verbose_name="Ubicación")
    photo_url = models.URLField(null=True, blank=True, verbose_name="URL de foto")
    created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Fecha de creación")
    coordinates = models.CharField(max_length=100, null=True, blank=True, verbose_name="Coordenadas")

    def __str__(self):
        return self.name or str(self.id)
    
class Product(models.Model):
    id = models.AutoField(primary_key=True,verbose_name="Nro de producto")
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products', verbose_name='Tienda')
    name = models.CharField(max_length=255, verbose_name="Nombre del producto")
    description = models.TextField(null=True, blank=True, verbose_name="Descripción")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio",validators=[MinValueValidator(Decimal('0.01'))])
    stock = models.IntegerField(default=0, verbose_name="Stock")
    photo_url = models.URLField(null=True, blank=True, verbose_name="URL de foto")

    def __str__(self):
        return f'{self.name}, de {self.store.name}' or str(self.id)