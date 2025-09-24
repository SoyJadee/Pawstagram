from django.core.management.base import BaseCommand
from tienda.models import Store

class Command(BaseCommand):
    help = 'Migra los datos del campo coordinates a latitude y longitude en Store.'

    def handle(self, *args, **options):
        count = 0
        for store in Store.objects.all():
            # Si el campo coordinates existía antes de la migración
            if hasattr(store, 'coordinates') and store.coordinates:
                try:
                    lat, lon = [float(x.strip()) for x in store.coordinates.split(',')]
                    store.latitude = lat
                    store.longitude = lon
                    store.save()
                    count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error en id {store.id}: {e}'))
        self.stdout.write(self.style.SUCCESS(f'Migración completada. {count} registros actualizados.'))
