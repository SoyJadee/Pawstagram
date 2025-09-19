from django.contrib import admin
from .models import Pet

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'creator_first_name', 'creator_last_name', 'breed', 'age', 'gender', 'is_available_for_adoption')
    list_filter = ('gender', 'is_available_for_adoption')
    search_fields = ('name', 'breed', 'description', 'creator__user__first_name', 'creator__user__last_name')

    @admin.display(description='Nombre creador')
    def creator_first_name(self, obj):
        return obj.creator.user.first_name if obj.creator and obj.creator.user else ''

    @admin.display(description='Apellido creador')
    def creator_last_name(self, obj):
        return obj.creator.user.last_name if obj.creator and obj.creator.user else ''