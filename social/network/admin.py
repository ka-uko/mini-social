from django.contrib import admin
from .models import Post, Comment, Like

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('created_at',)
    show_change_link = True

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'short_text', 'created_at')  # 👈 список колонок
    search_fields = ('text', 'author__username')
    list_filter = ('created_at', 'author')
    inlines = [CommentInline]

    def short_text(self, obj):
        return obj.text[:40]
    short_text.short_description = "Текст"

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'post', 'parent', 'created_at')
    search_fields = ('text', 'author__username')
    list_filter = ('created_at',)

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'created_at')
    list_filter = ('created_at', 'user')
