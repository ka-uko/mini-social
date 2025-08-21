from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Follow

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("id", "username", "email", "is_staff", "date_joined")
    search_fields = ("username", "email")
    list_filter = ("is_staff", "is_superuser", "is_active")
    ordering = ("-date_joined",)

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("id", "follower", "following", "created_at")
    search_fields = ("follower__username", "following__username")
    list_filter = ("created_at",)
    autocomplete_fields = ("follower", "following")
    readonly_fields = ("created_at",)

# Брендинг админки (можно перенести в любой из admin.py установленных приложений)
admin.site.site_header = "Админка БаняNet"
admin.site.site_title = "БаняNet Admin"
admin.site.index_title = "Управление мини-соцсетью"
