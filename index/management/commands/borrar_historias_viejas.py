from django.core.management.base import BaseCommand
from index.models import Histories
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Elimina historias con más de 24 horas de antigüedad.'

    def handle(self, *args, **options):
        limite = timezone.now() - timedelta(hours=24)
        historias_borradas, _ = Histories.objects.filter(
            created_at__lt=limite).delete()
        self.stdout.write(self.style.SUCCESS(
            f'Se eliminaron {historias_borradas} historias de más de 24 horas.'))
