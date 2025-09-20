from django.shortcuts import render, redirect
from .models import Like
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from mascota.models import Pet
from .models import Post, Comment, Notifications as Notification
from adopcion.forms import AdoptionForm
from adopcion.models import Adoption
from django.contrib import messages
from supabase import create_client
from django.conf import settings
import os
import uuid
import logging
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.timesince import timesince
# Endpoint AJAX para obtener notificaciones del usuario autenticado
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET


@login_required
@require_GET
def notificaciones_json(request):
    notificaciones = Notification.objects.filter(
        user=request.user).order_by('-created_at')[:30]
    data = []
    for n in notificaciones:
        # Si la notificación tiene post relacionado, obtener photo_url
        photo_url = None
        if hasattr(n, 'post') and n.post and hasattr(n.post, 'photo_url'):
            photo_url = n.post.photo_url
        data.append({
            'id': n.id,
            'type': n.type,
            'message': n.message,
            'is_read': n.is_read,
            'created_at': timesince(n.created_at) + ' atrás',
            'photo_url': photo_url,
        })
    return JsonResponse({'notificaciones': data}, encoder=DjangoJSONEncoder)


# Marcar notificaciones como leídas


@csrf_exempt
@require_POST
def marcar_notificaciones_leidas(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'not_authenticated'})
    Notification.objects.filter(
        user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'success': True})


@require_POST
def like_post(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'not_authenticated'})
    post_id = request.POST.get('post_id')
    if not post_id:
        return JsonResponse({'success': False, 'error': 'no_post'})
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'not_found'})
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
        # Crear notificación solo si el autor no es el mismo usuario
        if post.author != request.user:
            Notification.objects.create(
                post=post,
                user=post.author,
                referenceLike=like,
                type='like',
                message=f'{request.user.username} le dio like a tu post.',
                is_read=False
            )
    likes_count = Like.objects.filter(post=post).count()
    return JsonResponse({'success': True, 'liked': liked, 'likes': likes_count})


# Configurar logging
logger = logging.getLogger(__name__)

# Inicializar Supabase con manejo de errores
try:
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
except Exception as e:
    logger.error(f"Error al inicializar Supabase: {e}")
    supabase = None


def principal(request):
    # Eliminar comentarios con '{{' en el contenido (limpieza de datos)
    from .models import Comment
    # Limpieza de comentarios con '{{' (solo una vez, no en cada request en producción)
    if request.method == 'GET':
        Comment.objects.filter(content__contains='{{').delete()
    mascotas = []
    if request.user.is_authenticated:
        try:
            from usuarios.models import UserProfile
            user_profile = UserProfile.objects.filter(
                user=request.user).first()
            if user_profile:
                mascotas = Pet.objects.filter(creator=user_profile)
            else:
                mascotas = []
        except Exception as e:
            logger.error(f"Error al obtener mascotas del usuario: {e}")
            messages.error(request, 'Error al cargar tus mascotas.')

    form = AdoptionForm()
    adoption_success = False

    if request.method == 'POST':
        # Publicar un post
        if request.user.is_authenticated and 'mascota_id' in request.POST:
            try:
                mascota_id = request.POST.get('mascota_id')
                descripcion = request.POST.get('descripcion', '').strip()
                foto = request.FILES.get('foto')
                if not descripcion:
                    messages.error(request, 'Debes escribir una descripción.')
                    return redirect('principal')
                if not foto:
                    messages.error(request, 'Debes subir una foto.')
                    return redirect('principal')
                if foto.size > 5 * 1024 * 1024:
                    messages.error(
                        request, 'La imagen es demasiado grande. Máximo 5MB.')
                    return redirect('principal')
                allowed_types = ['image/jpeg',
                                 'image/png', 'image/gif', 'image/webp']
                if foto.content_type not in allowed_types:
                    messages.error(
                        request, 'Tipo de archivo no válido. Solo se permiten imágenes.')
                    return redirect('principal')
                user_profile = getattr(request.user, 'userprofile', None)
                if not user_profile:
                    messages.error(request, 'Perfil de usuario no encontrado.')
                    return redirect('principal')
                mascota = Pet.objects.filter(
                    idPet=mascota_id, creator=user_profile).first()
                if not mascota:
                    messages.error(
                        request, 'Mascota no encontrada o no tienes permisos.')
                    return redirect('principal')
                # Subir imagen a Supabase si está disponible
                url = None
                if supabase:
                    try:
                        usuario = request.user.username
                        nombre_mascota = mascota.name
                        nombre_archivo = f"{uuid.uuid4()}_{foto.name}"
                        ruta_supabase = f"{usuario}/{nombre_mascota}/{nombre_archivo}"
                        logger.info(
                            f'Subiendo imagen a Supabase: {ruta_supabase}')
                        foto_data = foto.read()
                        foto.seek(0)
                        res = supabase.storage.from_('Usuarios').upload(
                            ruta_supabase, foto_data, {'content-type': foto.content_type})
                        url_result = supabase.storage.from_(
                            'Usuarios').get_public_url(ruta_supabase)
                        if isinstance(url_result, dict) and 'publicUrl' in url_result:
                            url = url_result['publicUrl']
                        else:
                            url = url_result
                        if url and url.endswith('?'):
                            url = url[:-1]
                        logger.info(f'URL de imagen generada: {url}')
                    except Exception as e:
                        logger.error(f"Error al subir imagen a Supabase: {e}")
                        messages.error(
                            request, 'Error al subir la imagen. Inténtalo de nuevo.')
                        return redirect('principal')
                else:
                    messages.error(
                        request, 'Servicio de almacenamiento no disponible.')
                    return redirect('principal')
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
                messages.error(
                    request, 'Error al crear la publicación. Inténtalo de nuevo.')
            return redirect('principal')
        # Guardar comentario
        elif request.user.is_authenticated and 'comment_post_id' in request.POST:
            comment_content = request.POST.get('comment_content', '').strip()
            comment_post_id = request.POST.get('comment_post_id')
            if comment_content and comment_post_id:
                try:
                    post = Post.objects.get(id=comment_post_id)
                    comment = Comment.objects.create(
                        post=post,
                        user=request.user,
                        content=comment_content
                    )
                    # Crear notificación solo si el autor no es el mismo usuario
                    if post.author != request.user:
                        Notification.objects.create(
                            post=post,
                            user=post.author,
                            referenceComment=comment,
                            type='comment',
                            message=f'{request.user.username} comentó en tu post.',
                            is_read=False
                        )
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        from django.http import JsonResponse
                        return JsonResponse({
                            'success': True,
                            'username': request.user.username,
                            'content': comment_content
                        })
                    messages.success(request, 'Comentario publicado.')
                except Exception as e:
                    logger.error(f"Error al guardar el comentario: {e}")
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        from django.http import JsonResponse
                        return JsonResponse({'success': False})
                    messages.error(
                        request, 'No se pudo guardar el comentario.')
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                from django.http import JsonResponse
                return JsonResponse({'success': False})
            return redirect('principal')

        form = AdoptionForm(request.POST)
        if form.is_valid():
            try:
                adoption = form.save(commit=False)
                # obtener pet id enviado desde el modal (limpiar y manejar varios casos)
                pet_id = (request.POST.get('pet_id')
                          or request.POST.get('mascota_id') or '').strip()
                pet = None
                if pet_id:
                    # intentar por campo idPet (PK nombrado) primero
                    pet = Pet.objects.filter(idPet=pet_id).first()
                    if not pet:
                        # intentar por pk numérico por si se usa otra convención
                        try:
                            pet = Pet.objects.filter(pk=int(pet_id)).first()
                        except Exception:
                            pet = None
                if not pet:
                    logger.warning(
                        f"Solicitud de adopción: pet_id recibido='{pet_id}' no corresponde a ninguna Mascota")
                    messages.error(
                        request, 'Mascota inválida. No se pudo procesar la solicitud de adopción.')
                else:
                    adoption.pet = pet
                    # responsable es el creador de la mascota (UserProfile)
                    adoption.responsable = getattr(pet, 'creator', None)
                    adoption.status = 'pending'
                    adoption.save()
                    adoption_success = True
            except Exception as e:
                logger.error(f"Error al guardar adopción: {e}")
                messages.error(
                    request, 'Error al procesar la solicitud de adopción. Inténtalo de nuevo.')
            # No redirigir, mostrar mensaje en modal
        else:
            messages.error(
                request, 'Error en el formulario de adopción. Revisa los datos ingresados.')

    # GET request or after POST handling, always render the page
    posts = Post.objects.all().order_by('-created_at').prefetch_related(
        'comments__user', 'pet', 'author')
    context = {
        'mascotas_usuario': mascotas,
        'form': form,
        'posts': posts,
        'adoption_success': adoption_success,
    }
    return render(request, 'Principal.html', context)


def search(request):
    query = request.GET.get('q', '').strip()
    results = []
    if query:
        pets = Pet.objects.filter(name__icontains=query).select_related(
            'creator__user').order_by('-created_at')
        results = pets
    return render(request, 'search_results.html', {'query': query, 'results': pets})
