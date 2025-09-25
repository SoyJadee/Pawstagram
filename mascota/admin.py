from django.contrib import admin
from .models import Pet, Animals

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('idPet', 'name', 'creator__user__username', 'breed', 'age', 'gender', 'status')
    list_filter = ('gender', 'status')
    search_fields = ('name', 'breed', 'description', 'creator__user__first_name', 'creator__user__last_name')

    @admin.display(description='Nombre creador')
    def creator_first_name(self, obj):
        return obj.creator.user.first_name if obj.creator and obj.creator.user else ''

    @admin.display(description='Apellido creador')
    def creator_last_name(self, obj):
        return obj.creator.user.last_name if obj.creator and obj.creator.user else ''
    
@admin.register(Animals)
class AnimalsAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)
    @admin.display(description='Tipo de animal')
    def tipo_animal(self, obj):
        return obj.tipo.nombre if obj.tipo else ''