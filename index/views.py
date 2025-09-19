
from django.shortcuts import render, redirect
from mascota.models import Pet
from django.contrib import messages
from supabase import create_client
from django.conf import settings
import os
import uuid

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def userAuthenticated(request):
    return request.user.is_authenticated


def principal(request):
    mascotas = []
    if request.user.is_authenticated:
        user_profile = getattr(request.user, 'userprofile', None)
        if user_profile:
            mascotas = Pet.objects.filter(creator=user_profile)

    if request.method == 'POST' and request.user.is_authenticated:
        mascota_id = request.POST.get('mascota_id')
        descripcion = request.POST.get('descripcion')
        foto = request.FILES.get('foto')
        mascota = Pet.objects.filter(
            id=mascota_id, creator=user_profile).first()
        if not mascota or not foto or not descripcion:
            messages.error(
                request, 'Debes seleccionar una mascota, subir una foto y escribir una descripción.')
            return redirect('principal')

        usuario = request.user.username
        nombre_mascota = mascota.name

        nombre_archivo = f"{uuid.uuid4()}_{foto.name}"
        ruta_supabase = f"{usuario}/{nombre_mascota}/{nombre_archivo}"

        # Subir la imagen al bucket 'Usuarios'
        print('RUTA SUPABASE:', ruta_supabase)
        res = supabase.storage.from_('Usuarios').upload(
            ruta_supabase, foto.read(), {'content-type': foto.content_type})
        # Obtener URL pública (debug)
        url_result = supabase.storage.from_(
            'Usuarios').get_public_url(ruta_supabase)
        print('RESULTADO get_public_url:', url_result)
        # Intenta extraer la URL si es un dict, si no, usa el string
        if isinstance(url_result, dict) and 'publicUrl' in url_result:
            url = url_result['publicUrl']
        else:
            url = url_result
        # Eliminar '?' final si existe
        if url.endswith('?'):
            url = url[:-1]
        print('URL PUBLICO SUPABASE (final):', url)

        # Guardar el post en el modelo Post de Django
        from .models import Post
        post_obj = Post.objects.create(
            pet=mascota,
            author=request.user,
            content=descripcion,
            photo_url=url
        )

        messages.success(request, '¡Publicación realizada con éxito!')
        return redirect('principal')

    # Obtener los posts más recientes
    from .models import Post
    posts = Post.objects.select_related(
        'author', 'pet').order_by('-created_at')
    return render(request, 'Principal.html', {
        'user_authenticated': userAuthenticated(request),
        'mascotas_usuario': mascotas,
        'posts': posts
    })
