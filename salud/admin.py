from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import ServicesHealth, Service, Specialty
# Register your models here.

@admin.register(ServicesHealth)
class ServicesHealthAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner', 'consultPrice')
    search_fields = ('name', 'owner')
    list_filter = ('type',)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'serviceshealth')
    search_fields = ('name',)

@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'serviceshealth')
    search_fields = ('name',)
