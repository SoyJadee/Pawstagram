from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import ServicesHealth
# Register your models here.
@admin.register(ServicesHealth)
class ServicesHealthAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner', 'consultPrice')
    search_fields = ('name', 'owner')
    list_filter = ('type',)
