from django.contrib import admin
from .models import ServicesHealth

@admin.register(ServicesHealth)
class ServicesHealthAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'phone', 'consultPrice')
    list_editable = ('consultPrice',)
    search_fields = ('name', 'type', 'phone', 'email')
