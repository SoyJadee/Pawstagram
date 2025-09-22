from django.contrib import admin
from .models import Like, Comment, Post
# Register your models here.

admin.site.site_header = "Pawly Admin"
admin.site.site_title = "Pawly Admin Portal"

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
