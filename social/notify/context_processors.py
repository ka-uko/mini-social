def unread_notifications(request):
    if not request.user.is_authenticated:
        return {}
    return {
        'notify_unread': request.user.notifications.filter(is_read=False).count()
    }