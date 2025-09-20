from django.conf import settings
from adopcion.models import Adoption
from usuarios.models import UserProfile
from index.models import Post
from mascota.models import Pet
def user_authenticated(request):
    countPosts = Post.objects.count()
    countPets = Pet.objects.count()
    countUsers = UserProfile.objects.filter(user__is_active=True, user__is_staff=False,user__is_superuser=False).count()
    if request.user.is_authenticated:
        if not request.user.is_staff and not request.user.is_superuser:
            try:
                user_profile = UserProfile.objects.select_related('user').filter(user=request.user).first()
                if user_profile:
                    print(user_profile)
                    notificaciones = Adoption.objects.filter(responsable=user_profile.user.id, status='pending').select_related('pet','responsable__user').order_by('-created_at')
                else:
                    notificaciones = Adoption.objects.none()
            except Exception:
                notificaciones = Adoption.objects.none()
        else:
            notificaciones = []
        print("notificaciones:", notificaciones)
        return {
            'user_authenticated': True,
            'notificaciones': notificaciones
            ,'countPosts':countPosts
            ,'countPets':countPets
            ,'countUsers':countUsers
        }
    else:
        return {
            'user_authenticated': False,
            'notificaciones': None
            ,'countPosts':countPosts
            ,'countPets':countPets
            ,'countUsers':countUsers
        }
