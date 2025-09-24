from django.core.management.base import BaseCommand
from salud.models import ServicesHealth

class Command(BaseCommand):
    help = 'Migra los datos del campo coordinates a latitude y longitude.'

    def handle(self, *args, **options):
        count = 0
        for service in ServicesHealth.objects.all():
            # Si el campo coordinates existía antes de la migración
            if hasattr(service, 'coordinates') and service.coordinates:
                try:
                    lat, lon = [float(x.strip()) for x in service.coordinates.split(',')]
                    service.latitude = lat
                    service.longitude = lon
                    service.save()
                    count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error en id {service.id}: {e}'))
        self.stdout.write(self.style.SUCCESS(f'Migración completada. {count} registros actualizados.'))
