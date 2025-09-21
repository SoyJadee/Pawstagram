from django.shortcuts import render, get_object_or_404, redirect
from .models import Pet
from index.models import Post, Comment, Like
from index.forms import CommentForm
from adopcion.models import Adoption
from adopcion.forms import AdoptionForm
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
import logging
# Create your views here.


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
    likes_count = Like.objects.filter(post=post).count()
    return JsonResponse({'success': True, 'liked': liked, 'likes': likes_count})


# Configurar logging
logger = logging.getLogger(__name__)

def mascotaDetailsView(request, idPet):
    mascota = get_object_or_404(Pet, idPet=idPet)
    # Obtener posts relacionados a la mascota (por instancia)
    posts = Post.objects.filter(pet=mascota).order_by('-created_at').all()
    comentarios = {}
    likes = {}
    user_liked_post_ids = set()
    if request.user.is_authenticated:
        user_liked_post_ids = set(
            Like.objects.filter(user=request.user, post__in=posts).values_list(
                'post_id', flat=True)
        )
    for post in posts:
        comentarios[post.id] = Comment.objects.filter(post=post).all()
        likes[post.id] = Like.objects.filter(post=post).count()

    form = CommentForm()
    adoption_form = AdoptionForm()

    if request.method == "POST":
        # Distinguir qué formulario se envió con un input name distinto si es necesario
        form = CommentForm(request.POST)
        adoption_form = AdoptionForm(request.POST)

        if request.user.is_authenticated and 'comment_post_id' in request.POST:
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
                    # Notificación eliminada para evitar error de importación
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
            return redirect('perfil_mascota', idPet=mascota.idPet)

        if adoption_form.is_valid():
            try:
                new_adoption = adoption_form.save(commit=False)
                # permitir pet_id desde POST si viene del modal
                pet_id = (request.POST.get('pet_id') or '').strip()
                pet_obj = None
                if pet_id:
                    # intentar por idPet primero (clave primaria personalizada)
                    pet_obj = Pet.objects.filter(idPet=pet_id).first()
                    if not pet_obj:
                        try:
                            pet_obj = Pet.objects.filter(
                                pk=int(pet_id)).first()
                        except Exception:
                            pet_obj = None
                if pet_id and not pet_obj:
                    logger.warning(
                        f"Solicitud de adopción (perfil): pet_id recibido='{pet_id}' no corresponde a ninguna Mascota")
                    messages.error(request, 'Mascota no válida para adopción.')
                    return redirect('perfil_mascota', idPet=mascota.idPet)
                if pet_obj:
                    new_adoption.pet = pet_obj
                else:
                    new_adoption.pet = mascota

                pet_obj.status = new_adoption.status or 'pending'
                new_adoption.save()
                pet_obj.save()
                adoption_form = AdoptionForm()  # Resetear el formulario después de guardar
                messages.success(
                    request, 'Solicitud de adopción enviada correctamente.')
            except Exception as e:
                logger.error(
                    f"Error al guardar adopción en vista mascota: {e}")
                messages.error(
                    request, 'Error al procesar la solicitud de adopción.')

    return render(
        request,
        "perfilMascota.html",
        {
            "mascota": mascota,
            "posts": posts,
            "comentarios": comentarios,
            "likes": likes,
            "form": form,
            "adoption_form": adoption_form,
            "user_liked_post_ids": user_liked_post_ids,
        },
    )
