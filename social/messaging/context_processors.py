from django.db.models import Q
from .models import Message

def unread_messages(request):
    """
    Возвращает:
      - unread_count: общее число непрочитанных входящих сообщений для текущего пользователя
      - has_unread: флаг наличия непрочитанных
    """
    if not request.user.is_authenticated:
        return {}

    user = request.user
    count = (
        Message.objects
        .filter(Q(thread__user1=user) | Q(thread__user2=user))  # диалоги где я участник
        .filter(~Q(sender=user), read_at__isnull=True)          # входящие, ещё не прочитанные
        .count()
    )
    return {"unread_count": count, "has_unread": count > 0}
