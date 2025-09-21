from django.contrib import admin
from .models import Adoption


# Register your models here.
@admin.register(Adoption)
class AdoptionAdmin(admin.ModelAdmin):
    list_display = ("id", "pet", "pet__creator", "created_at")
    list_filter = ("created_at",)
    search_fields = (
        "pet__name",
        "pet__creator__user__username",
    )

    @admin.display(description="Responsable")
    def responsable_username(self, obj):
        return (
            obj.responsable.user.username
            if obj.responsable and obj.responsable.user
            else ""
        )

    @admin.display(description="Mascota")
    def pet_name(self, obj):
        return obj.pet.name if obj.pet else ""
