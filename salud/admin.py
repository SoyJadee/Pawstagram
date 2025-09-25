# Register your models here.
from django.contrib import admin
from .models import ServicesHealth, Service, Specialty, Reviews
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

@admin.register(Reviews)
class ReviewsAdmin(admin.ModelAdmin):
    list_display = ('id', 'service', 'rating', 'comment', 'created_at')
    search_fields = ('service__name', 'comment')
    list_filter = ('rating', 'created_at')
