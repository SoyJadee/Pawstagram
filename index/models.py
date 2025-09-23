from django.db import models
from usuarios.models import UserProfile
from django.contrib.auth.models import User
from mascota.models import Pet


class Post(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID de post")
    pet = models.ForeignKey(
        Pet,
        on_delete=models.CASCADE,
        verbose_name="mascota",
        related_name="index_posts",
    )
    author = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        verbose_name="autor",
        related_name="index_posts",
    )
    content = models.TextField(
        max_length=300, null=True, blank=True, verbose_name="Contenido del post"
    )
    photo_url = models.URLField(null=True, blank=True, verbose_name="URL de la foto")
    photo_storage_path = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Ruta de almacenamiento de la foto",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, null=True, verbose_name="Fecha de creación"
    )

    def __str__(self):
        return f"Post de {self.author} - {self.created_at}"


class Like(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID de like")
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="likes", verbose_name="post"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="likes", verbose_name="usuario"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, null=True, verbose_name="Fecha de creación"
    )

    def __str__(self):
        return f"Like de {self.user} en post {self.post_id}"


class Comment(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID de comentario")
    content = models.TextField(
        null=True, blank=True, verbose_name="Contenido del comentario"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        db_column="user_id",
        verbose_name="usuario",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        db_column="post_id",
        verbose_name="post",
    )

    class Meta:
        db_table = "index_comment"

    def __str__(self):
        return f"Comentario de {self.user} en post {self.post_id}"


class Notifications(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID de notificación")
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="post relacionado",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="usuario de la acción",
    )
    referenceLike = models.ForeignKey(
        Like,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
        verbose_name="like relacionado",
    )
    referenceComment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
        verbose_name="comentario relacionado",
    )
    type = models.CharField(
        max_length=50,
        verbose_name="tipo",
        choices=[("like", "Like"), ("comment", "Comentario")],
    )
    message = models.CharField(max_length=255, verbose_name="mensaje")
    is_read = models.BooleanField(default=False, verbose_name="leído")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="fecha de creación"
    )

    def __str__(self):
        return (
            f"Notificación para {self.user} - {'Leído' if self.is_read else 'No leído'}"
        )


class Histories(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID de historia")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="usuario", related_name="histories"
    )
    photo_url = models.URLField(null=True, blank=True, verbose_name="URL de la foto")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación"
    )

    def __str__(self):
        return f"Historia de {self.author} - {self.created_at}"
