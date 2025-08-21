from django.contrib import admin
from .models import Thread, Message

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('created_at', 'read_at', 'sender')

@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'user1', 'user2', 'updated_at', 'created_at')
    search_fields = ('user1__username', 'user2__username')
    list_filter = ('updated_at', 'created_at')
    inlines = [MessageInline]

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'thread', 'sender', 'short_text', 'created_at', 'read_at')
    search_fields = ('text', 'sender__username', 'thread__user1__username', 'thread__user2__username')
    list_filter = ('created_at',)
    autocomplete_fields = ('thread', 'sender')

    def short_text(self, obj):
        return (obj.text[:60] + '…') if len(obj.text) > 60 else obj.text
    short_text.short_description = 'Текст'
