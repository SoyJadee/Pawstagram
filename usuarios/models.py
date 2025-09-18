from django.db import models
from django.contrib.auth.models import User
import uuid

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=30, null=True, blank=True)
    profile_photo_url = models.URLField(null=True, blank=True)
    is_foundation = models.BooleanField(default=False, null=True)

    def __str__(self):
        return self.user.email or self.user.username