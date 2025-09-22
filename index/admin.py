from django.contrib import admin
from .models import Like, Comment, Post
# Register your models here.

admin.site.site_header = "Pawly Admin"
admin.site.site_title = "Pawly Admin Portal"


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'pet_name', 'author_first_name', 'author_last_name', 'created_at')
    search_fields = ('author__username', 'pet__name', 'content')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

    @admin.display(description='Mascota')
    def pet_name(self, obj):
        return obj.pet.name if obj.pet else ''

    @admin.display(description='Nombre autor')
    def author_first_name(self, obj):
        return obj.author.first_name if obj.author else ''

    @admin.display(description='Apellido autor')
    def author_last_name(self, obj):
        return obj.author.last_name if obj.author else ''



@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_first_name', 'user_last_name', 'post', 'created_at')
    search_fields = ('user__username', 'post__content')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

    @admin.display(description='Nombre usuario')
    def user_first_name(self, obj):
        return obj.user.first_name if obj.user else ''

    @admin.display(description='Apellido usuario')
    def user_last_name(self, obj):
        return obj.user.last_name if obj.user else ''



@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_first_name', 'user_last_name', 'content')
    search_fields = ('user__username', 'post__content', 'content')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

    @admin.display(description='Nombre usuario')
    def user_first_name(self, obj):
        return obj.user.first_name if obj.user else ''

    @admin.display(description='Apellido usuario')
    def user_last_name(self, obj):
        return obj.user.last_name if obj.user else ''
