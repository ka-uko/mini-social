from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView

from .forms import SignupForm, ProfileForm
from .models import User, Follow
from network.models import Post
from notify.models import Notification


class SignupView(CreateView):
    form_class = SignupForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        response = super().form_valid(form)
        # авто-логин после регистрации
        login(self.request, self.object)
        return response


def profile(request, username: str):
    """
    Страница профиля пользователя с его постами и кнопкой подписки.
    """
    # сразу подтянем специализации (M2M), чтобы избежать лишних запросов в шаблоне
    profile_user = get_object_or_404(
        User.objects.prefetch_related("services"),
        username=username,
    )

    posts = (
        Post.objects
        .filter(author=profile_user)
        .select_related("author")
        .prefetch_related("likes", "comments")
        .all()
    )

    stats = {
        "followers_count": Follow.objects.filter(following=profile_user).count(),
        "following_count": Follow.objects.filter(follower=profile_user).count(),
        "posts_count": posts.count(),
    }

    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_following = Follow.objects.filter(
            follower=request.user, following=profile_user
        ).exists()

    return render(
        request,
        "profile.html",
        {
            "profile_user": profile_user,
            "posts": posts,
            "stats": stats,
            "is_following": is_following,
        },
    )


@login_required
def profile_edit(request, username: str):
    """
    Редактирование собственного профиля.
    """
    profile_user = get_object_or_404(User, username=username)
    if request.user != profile_user:
        messages.error(request, "Можно редактировать только свой профиль.")
        return redirect("profile", username=profile_user.username)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile_user)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль обновлён.")
            return redirect("profile", username=profile_user.username)
    else:
        form = ProfileForm(instance=profile_user)

    return render(
        request,
        "accounts/profile_edit.html",
        {"profile_user": profile_user, "form": form},
    )


@login_required
def toggle_follow(request, username: str):
    """
    Подписаться/отписаться на пользователя. Работает по POST.
    Создаёт уведомление для целевого пользователя при новой подписке.
    """
    if request.method != "POST":
        return redirect("profile", username=username)

    target = get_object_or_404(User, username=username)
    if target == request.user:
        messages.error(request, "Нельзя подписаться на себя.")
        return redirect("profile", username=username)

    obj, created = Follow.objects.get_or_create(
        follower=request.user, following=target
    )
    if created:
        messages.success(request, f"Вы подписались на @{target.username}.")
        # уведомление о новой подписке
        try:
            Notification.objects.create(
                to_user=target,
                verb="follow",
                actor=request.user,
            )
        except Exception:
            # Если notify не настроен/временно недоступен — не ломаем флоу
            pass
    else:
        obj.delete()
        messages.info(request, f"Вы отписались от @{target.username}.")

    next_url = request.POST.get("next") or reverse("profile", args=[username])
    return redirect(next_url)


def followers_list(request, username: str):
    """
    Список подписчиков пользователя.
    """
    profile_user = get_object_or_404(User, username=username)
    followers = (
        Follow.objects
        .filter(following=profile_user)
        .select_related("follower")
        .all()
    )
    return render(
        request,
        "followers_list.html",
        {"profile_user": profile_user, "followers": followers},
    )


def following_list(request, username: str):
    """
    Список, на кого пользователь подписан.
    """
    profile_user = get_object_or_404(User, username=username)
    following = (
        Follow.objects
        .filter(follower=profile_user)
        .select_related("following")
        .all()
    )
    return render(
        request,
        "following_list.html",
        {"profile_user": profile_user, "following": following},
    )





