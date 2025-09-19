from django.contrib import admin
from .models import Adoption
# Register your models here.
@admin.register(Adoption)
class AdoptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'pet', 'adopter', 'status',)
    list_filter = ('status',)
    search_fields = ('pet__name', 'adopter__username', 'status')
    list_editable = ('status',)