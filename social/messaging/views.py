from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import now

from accounts.models import User
from .models import Thread, Message
from .forms import MessageForm



@login_required
def inbox(request):
    threads = (
        Thread.objects
        .filter(Q(user1=request.user) | Q(user2=request.user))
        .select_related('user1', 'user2')
        .annotate(
            unread_count=Count(
                'messages',
                filter=Q(messages__read_at__isnull=True) & ~Q(messages__sender=request.user),
                distinct=True,
            )
        )
        .order_by('-updated_at')
    )
    return render(request, 'messaging/inbox.html', {'threads': threads})


@login_required
def start_thread(request, username):
    """
    Начать (или открыть существующий) диалог с пользователем `username`.
    """
    target = get_object_or_404(User, username=username)
    if target == request.user:
        messages.error(request, "Нельзя писать самому себе.")
        return redirect("profile", username=username)

    # нормализуем порядок id для поиска существующего треда
    u1, u2 = (request.user, target) if request.user.id < target.id else (target, request.user)
    thread = Thread.objects.filter(user1=u1, user2=u2).first()
    if not thread:
        thread = Thread.objects.create(user1=u1, user2=u2)

    return redirect("thread_detail", pk=thread.pk)


@login_required
def thread_detail(request, pk):
    """
    Страница переписки. Показывает сообщения + форма отправки.
    Доступ только участникам диалога.
    """
    thread = get_object_or_404(
        Thread.objects.select_related("user1", "user2"),
        pk=pk
    )
    if request.user not in thread.participants():
        messages.error(request, "Доступ к этому диалогу запрещён.")
        return redirect("inbox")

    # Загружаем сообщения
    msgs = thread.messages.select_related("sender").all()

    # Отмечаем входящие как прочитанные
    unread = msgs.filter(~Q(sender=request.user), read_at__isnull=True)
    if unread.exists():
        unread.update(read_at=now())

    # Отправка нового сообщения
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.thread = thread
            msg.sender = request.user
            msg.save()
            # Обновим updated_at у треда (Message.save это не делает)
            Thread.objects.filter(pk=thread.pk).update(updated_at=now())
            return redirect("thread_detail", pk=thread.pk)
    else:
        form = MessageForm()

    other = thread.other(request.user)
    return render(
        request,
        "messaging/thread_detail.html",
        {
            "thread": thread,
            "msgs": msgs,   #
            "form": form,
            "other": other,
        },
    )




