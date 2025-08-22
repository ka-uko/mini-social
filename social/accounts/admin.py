from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, ServiceTag, Follow

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Личная информация", {"fields": ("first_name", "last_name", "email")}),
        ("Профиль", {"fields": ("avatar", "bio", "role", "services", "city")}),
        ("Права доступа", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Даты", {"fields": ("last_login", "date_joined")}),
    )
    list_display = ("username", "email", "role", "city", "is_staff")
    list_filter = ("role", "is_staff", "is_superuser", "is_active", "groups")
    filter_horizontal = ("groups", "user_permissions", "services")

@admin.register(ServiceTag)
class ServiceTagAdmin(admin.ModelAdmin):
    list_display = ("code", "title")
    search_fields = ("code", "title")

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("follower", "following", "created_at")
    search_fields = ("follower__username", "following__username")
