from django.shortcuts import render, get_object_or_404
from .models import Pet
from index.models import Post, Comment, Like
from index.forms import CommentForm
from adopcion.models import Adoption
from adopcion.forms import AdoptionForm

# Create your views here.
def mascotaDetailsView(request, pet_id):
    mascota = get_object_or_404(Pet, id=pet_id)
    posts = Post.objects.filter(pet=mascota).all()
    comentarios = {}
    likes = {}
    for post in posts:
        comentarios[post.id] = Comment.objects.filter(post=post).all()
        likes[post.id] = Like.objects.filter(post=post).count()

    form = CommentForm()
    adoption_form = AdoptionForm()

    if request.method == "POST":
        # Distinguir qué formulario se envió con un input name distinto si es necesario
        form = CommentForm(request.POST)
        adoption_form = AdoptionForm(request.POST)

        post_id = request.POST.get("post") or request.POST.get("post_id")
        if post_id and form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.user = getattr(request.user, 'userprofile', None) or request.user
            new_comment.post = get_object_or_404(Post, id=post_id)
            new_comment.save()
            form = CommentForm()  # Resetear el formulario después de guardar

        if adoption_form.is_valid():
            new_adoption = adoption_form.save(commit=False)
            # adopter es un UserProfile en el modelo Adoption
            new_adoption.adopter = getattr(request.user, 'userprofile', None)
            new_adoption.pet = mascota
            # si el modelo Adoption usa choices con 'pending', asegúrate que exista
            try:
                new_adoption.status = new_adoption.status or 'pending'
            except Exception:
                pass
            new_adoption.save()
            adoption_form = AdoptionForm()  # Resetear el formulario después de guardar
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
        },
    )
