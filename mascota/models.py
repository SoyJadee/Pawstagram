from django.db import models
class Pet(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID de mascota")
    owner = models.ForeignKey('users.User', null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=20,verbose_name="Nombre")
    description = models.TextField(null=True, blank=True,verbose_name="Descripción")
    profile_photo_url = models.TextField(null=True, blank=True,verbose_name="URL de foto de perfil")
    is_available_for_adoption = models.BooleanField(default=False,verbose_name="Disponible para adopción")
    created_at = models.DateTimeField(auto_now_add=True,verbose_name="Fecha de creación")