
from django.shortcuts import render, redirect
from mascota.models import Pet
from .models import Post
from adopcion.forms import AdoptionForm
from adopcion.models import Adoption
from django.contrib import messages
from supabase import create_client
from django.conf import settings
import os
import uuid
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Inicializar Supabase con manejo de errores
try:
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
except Exception as e:
    logger.error(f"Error al inicializar Supabase: {e}")
    supabase = None


def principal(request):
    mascotas = []
    if request.user.is_authenticated:
        try:
            user_profile = getattr(request.user, 'userprofile', None)
            if user_profile:
                mascotas = Pet.objects.filter(creator=user_profile)
        except Exception as e:
            logger.error(f"Error al obtener mascotas del usuario: {e}")
            messages.error(request, 'Error al cargar tus mascotas.')
    
    form = AdoptionForm()
    
    if request.method == 'POST':
        if request.user.is_authenticated:
            try:
                mascota_id = request.POST.get('mascota_id')
                descripcion = request.POST.get('descripcion', '').strip()
                foto = request.FILES.get('foto')
                
                # Validaciones
                if not mascota_id:
                    messages.error(request, 'Debes seleccionar una mascota.')
                    return redirect('principal')
                
                if not descripcion:
                    messages.error(request, 'Debes escribir una descripción.')
                    return redirect('principal')
                    
                if not foto:
                    messages.error(request, 'Debes subir una foto.')
                    return redirect('principal')
                
                # Validar tamaño de imagen (máximo 5MB)
                if foto.size > 5 * 1024 * 1024:
                    messages.error(request, 'La imagen es demasiado grande. Máximo 5MB.')
                    return redirect('principal')
                
                # Validar tipo de archivo
                allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
                if foto.content_type not in allowed_types:
                    messages.error(request, 'Tipo de archivo no válido. Solo se permiten imágenes.')
                    return redirect('principal')

                user_profile = getattr(request.user, 'userprofile', None)
                if not user_profile:
                    messages.error(request, 'Perfil de usuario no encontrado.')
                    return redirect('principal')
                    
                mascota = Pet.objects.filter(id=mascota_id, creator=user_profile).first()
                if not mascota:
                    messages.error(request, 'Mascota no encontrada o no tienes permisos.')
                    return redirect('principal')

                # Subir imagen a Supabase si está disponible
                url = None
                if supabase:
                    try:
                        usuario = request.user.username
                        nombre_mascota = mascota.name
                        nombre_archivo = f"{uuid.uuid4()}_{foto.name}"
                        ruta_supabase = f"{usuario}/{nombre_mascota}/{nombre_archivo}"

                        logger.info(f'Subiendo imagen a Supabase: {ruta_supabase}')
                        
                        # Leer el archivo
                        foto_data = foto.read()
                        foto.seek(0)  # Reset file pointer
                        
                        # Subir la imagen al bucket 'Usuarios'
                        res = supabase.storage.from_('Usuarios').upload(
                            ruta_supabase, foto_data, {'content-type': foto.content_type})
                        
                        # Obtener URL pública
                        url_result = supabase.storage.from_('Usuarios').get_public_url(ruta_supabase)
                        
                        # Procesar la URL
                        if isinstance(url_result, dict) and 'publicUrl' in url_result:
                            url = url_result['publicUrl']
                        else:
                            url = url_result
                        
                        # Limpiar la URL
                        if url and url.endswith('?'):
                            url = url[:-1]
                            
                        logger.info(f'URL de imagen generada: {url}')
                        
                    except Exception as e:
                        logger.error(f"Error al subir imagen a Supabase: {e}")
                        messages.error(request, 'Error al subir la imagen. Inténtalo de nuevo.')
                        return redirect('principal')
                else:
                    messages.error(request, 'Servicio de almacenamiento no disponible.')
                    return redirect('principal')

                # Guardar el post en la base de datos
                post_obj = Post.objects.create(
                    pet=mascota,
                    author=request.user,
                    content=descripcion,
                    photo_url=url
                )

                messages.success(request, '¡Publicación realizada con éxito!')
                logger.info(f'Post creado exitosamente: {post_obj.id}')
                
            except Exception as e:
                logger.error(f"Error al crear el post: {e}")
                messages.error(request, 'Error al crear la publicación. Inténtalo de nuevo.')
            
            return redirect('principal')
        form = AdoptionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Formulario de adopción enviado con éxito.')
            return redirect('principal')
        else:
            messages.error(request, 'Error en el formulario de adopción. Revisa los datos ingresados.')

    # Obtener los posts más recientes
    try:
        posts = Post.objects.select_related('author', 'pet').order_by('-created_at')
    except Exception as e:
        logger.error(f"Error al obtener posts: {e}")
        posts = []
        messages.error(request, 'Error al cargar las publicaciones.')
    
    return render(request, 'Principal.html', {
        'mascotas_usuario': mascotas,
        'posts': posts,
        'adoption_form': form,
    })
