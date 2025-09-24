from django.core.management.base import BaseCommand
from tienda.models import Store

class Command(BaseCommand):
    help = 'Corrige los valores de latitud y longitud reemplazando comas por puntos.'

    def handle(self, *args, **options):
        count = 0
        for store in Store.objects.all():
            lat = store.latitude
            lon = store.longitude
            updated = False
            # Si el valor es string y contiene coma, reemplazar por punto
            if isinstance(lat, str) and ',' in lat:
                try:
                    store.latitude = float(lat.replace(',', '.'))
                    updated = True
                except Exception:
                    pass
            if isinstance(lon, str) and ',' in lon:
                try:
                    store.longitude = float(lon.replace(',', '.'))
                    updated = True
                except Exception:
                    pass
            if updated:
                store.save()
                count += 1
        self.stdout.write(self.style.SUCCESS(f'Corrección completada. {count} registros actualizados.'))
