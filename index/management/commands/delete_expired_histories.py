import logging
from supabase import create_client
from django.conf import settings
from index.models import Histories
import os
import django
import sys
from datetime import timedelta
from django.utils import timezone

# Ajusta la ruta al proyecto si es necesario
django.setup()

logger = logging.getLogger(__name__)

# Inicializar Supabase
supabase = None
try:
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
except Exception as e:
    logger.error(f"Error al inicializar Supabase: {e}")
    supabase = None


def delete_expired_histories():
    now = timezone.now()
    expired = Histories.objects.filter(
        created_at__lt=now - timedelta(hours=24))
    for historia in expired:
        # Borrar archivo de Supabase Storage
        if supabase and historia.photo_url:
            try:
                # Extraer la ruta relativa del archivo desde la URL pública
                # Ejemplo: https://.../storage/v1/object/public/Usuarios/usuario/histories/archivo.jpg
                path = historia.photo_url.split(
                    '/storage/v1/object/public/Usuarios/')[-1]
                supabase.storage.from_('Usuarios').remove([path])
            except Exception as e:
                logger.error(f"Error al borrar archivo de Supabase: {e}")
        historia.delete()
    print(f"Eliminadas {expired.count()} historias expiradas.")


if __name__ == "__main__":
    delete_expired_histories()
