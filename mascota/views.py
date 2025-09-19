from django.shortcuts import render
from .models import Pet
from index.models import Post,Comment,Like
from index.forms import CommentForm
from datetime import datetime as date
# Create your views here.
def mascotaDetailsView(request, pet_id):
    mascota = Pet.objects.filter(id=pet_id).first()
    posts = Post.objects.filter(pet=mascota).all()
    comentarios = {}
    likes = {}
    for post in posts:
        comentarios[post.id] = Comment.objects.filter(post=post).all()
        likes[post.id] = Like.objects.filter(post=post).count()

    form = CommentForm()

    if request.method == 'POST':
        form = CommentForm(request.POST)
        post_id = request.POST.get('post_id')
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.user = request.user
            new_comment.post_id = post_id
            new_comment.save()
            new_comment.created_at = date.now()
            form = CommentForm()  # Resetear el formulario después de guardar
    return render(request, 'perfilMascota.html', {'mascota': mascota, 'posts': posts, 'comentarios': comentarios, 'likes': likes, 'form': form})