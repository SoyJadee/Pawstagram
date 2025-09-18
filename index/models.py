from django.db import models
from usuarios.models import User
from mascota.models import Pet

class Post(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID de post")
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, verbose_name='mascota')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='autor')
    content = models.TextField(null=True, blank=True, verbose_name="Contenido del post")
    photo_url = models.URLField(null=True, blank=True, verbose_name="URL de la foto")
    created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Fecha de creación")

    def __str__(self):
        return f"Post de {self.author} - {self.created_at}"

class Like(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID de like")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes', verbose_name='post')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes', verbose_name='usuario')
    created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Fecha de creación")

    def __str__(self):
        return f"Like de {self.user} en post {self.post_id}"

class Comment(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID de comentario")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name='post')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name='usuario')
    content = models.TextField(null=True, blank=True, verbose_name="Contenido del comentario")
    created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Fecha de creación")

    def __str__(self):
        return f"Comentario de {self.user} en post {self.post_id}"