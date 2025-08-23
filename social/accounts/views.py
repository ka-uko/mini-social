from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView
from django.db.models import Count

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
    Страница профиля пользователя с его постами, подпиской
    и корректным отображением специализаций по выбранной роли.
    """
    profile_user = get_object_or_404(User, username=username)

    posts = (
        Post.objects
        .filter(author=profile_user)
        .select_related('author')
        .prefetch_related('likes', 'comments')
        .all()
    )

    stats = {
        'followers_count': Follow.objects.filter(following=profile_user).count(),
        'following_count': Follow.objects.filter(follower=profile_user).count(),
        'posts_count': posts.count(),
    }

    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_following = Follow.objects.filter(
            follower=request.user, following=profile_user
        ).exists()

    # ----- НОВОЕ: нормализуем отображение роли + специализаций -----
    # Человеческая подпись роли
    role_labels = {
        'provider': 'Банные услуги',
        'builder': 'Строительство бань',
        'seller': 'Продажа товаров',
        'enthusiast': 'Люблю попариться',
        '': '',
        None: '',
    }
    role_label = role_labels.get(profile_user.role, '')

    # Коды тегов по группам (должны совпадать с тем, что используешь в формах/JS)
    provider_codes = {'steam_master', 'massage', 'rent_bath'}
    builder_codes  = {'build', 'consult_build'}
    seller_codes   = {'brooms', 'clothes', 'accessories', 'cosmetics'}

    role_to_codes = {
        'provider': provider_codes,
        'builder': builder_codes,
        'seller': seller_codes,
    }

    allowed_codes = role_to_codes.get(profile_user.role, set())

    # Показываем ТОЛЬКО теги, соответствующие текущей роли
    if allowed_codes:
        services_for_role = (
            profile_user.services
            .filter(code__in=allowed_codes)
            .order_by('title')
        )
    else:
        services_for_role = profile_user.services.none()

    return render(request, 'profile.html', {
        'profile_user': profile_user,
        'posts': posts,
        'stats': stats,
        'is_following': is_following,
        'role_label': role_label,                     # <-- добавили
        'services_for_role': services_for_role,       # <-- добавили
    })


@login_required
def profile_edit(request, username):
    profile_user = get_object_or_404(User, username=username)
    if request.user != profile_user:
        messages.error(request, "Можно редактировать только свой профиль.")
        return redirect("profile", username=profile_user.username)

    if request.method == "POST":
        # Кнопка "Удалить фото"
        if request.POST.get("clear_avatar") == "1":
            if profile_user.avatar:
                profile_user.avatar.delete(save=False)
                profile_user.avatar = None
                profile_user.save(update_fields=["avatar"])
                messages.success(request, "Аватар удалён.")
            else:
                messages.info(request, "Аватар уже отсутствует.")
            return redirect("profile_edit", username=profile_user.username)

        form = ProfileForm(request.POST, request.FILES, instance=profile_user)
        # выбранные ids из POST (нужны, если форма не пройдет валидацию)
        try:
            selected_service_ids = list(map(str, form["services"].value() or []))
        except Exception:
            selected_service_ids = []
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль обновлён.")
            return redirect("profile", username=profile_user.username)
    else:
        form = ProfileForm(instance=profile_user)
        # выбранные ids из БД (GET)
        selected_service_ids = list(
            map(str, profile_user.services.values_list("id", flat=True))
        )

    return render(
        request,
        "accounts/profile_edit.html",
        {
            "profile_user": profile_user,
            "form": form,
            "selected_service_ids": selected_service_ids,  # <-- ВАЖНО
        },
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





