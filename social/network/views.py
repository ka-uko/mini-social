# network/views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import CommentForm, PostForm
from .models import Comment, Like, Post

from accounts.models import Follow, User
from notify.models import Notification


def home(request):
    feed = request.GET.get("feed")  # None | 'sub'

    if request.user.is_authenticated and feed == "sub":
        following_ids = Follow.objects.filter(
            follower=request.user
        ).values_list("following_id", flat=True)

        posts = (
            Post.objects.filter(author_id__in=following_ids)
            .select_related("author")
            .prefetch_related("likes", "comments__author")
        )
    else:
        posts = (
            Post.objects.select_related("author")
            .prefetch_related("likes", "comments__author")
        )

    # набор id постов, которые лайкнул текущий пользователь (для красного сердечка)
    if request.user.is_authenticated:
        liked_post_ids = set(
            Like.objects.filter(user=request.user, post_id__in=posts.values("id"))
            .values_list("post_id", flat=True)
        )
    else:
        liked_post_ids = set()

    form = PostForm() if request.user.is_authenticated else None
    return render(
        request,
        "home.html",
        {"posts": posts, "form": form, "feed": feed, "liked_post_ids": liked_post_ids},
    )


def search(request):
    q = request.GET.get("q", "").strip()
    users = posts = []
    if q:
        users = (
            User.objects.filter(
                Q(username__icontains=q)
                | Q(first_name__icontains=q)
                | Q(last_name__icontains=q)
                | Q(city__icontains=q)
            )
            .order_by("username")[:50]
        )
        posts = (
            Post.objects.filter(Q(text__icontains=q) | Q(author__username__icontains=q))
            .select_related("author")
            .order_by("-created_at")[:50]
        )
    return render(request, "search.html", {"q": q, "users": users, "posts": posts})


@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, "Пост создан.")
            return redirect("post_detail", pk=post.pk)
    else:
        form = PostForm()
    return render(request, "post_form.html", {"form": form, "title": "Новый пост"})


def post_detail(request, pk):
    post = get_object_or_404(Post.objects.select_related("author"), pk=pk)
    comments = (
        post.comments.select_related("author", "parent")
        .prefetch_related("replies__author", "replies__replies__author")
        .all()
    )
    comment_form = CommentForm() if request.user.is_authenticated else None
    user_liked = request.user.is_authenticated and post.likes.filter(
        user=request.user
    ).exists()
    return render(
        request,
        "post_detail.html",
        {
            "post": post,
            "comments": comments,
            "comment_form": comment_form,
            "user_liked": user_liked,
        },
    )


@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Пост обновлён.")
            return redirect("post_detail", pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(
        request, "post_form.html", {"form": form, "title": "Редактировать пост"}
    )


@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == "POST":
        post.delete()
        messages.success(request, "Пост удалён.")
        return redirect(request.POST.get("next") or "home")
    return render(request, "post_confirm_delete.html", {"post": post})


@login_required
@require_POST
def toggle_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(user=request.user, post=post)

    if not created:
        # снятие лайка
        like.delete()
        messages.info(request, "Лайк убран.")
    else:
        # поставили лайк
        messages.success(request, "Пост понравился.")
        # уведомляем автора, если лайк не на свой пост
        if post.author_id != request.user.id:
            try:
                Notification.objects.create(
                    to_user=post.author,
                    verb="like",
                    actor=request.user,
                    post_id=post.id,
                )
            except Exception:
                # не ломаем поток, если notify недоступен
                pass

    return redirect(request.POST.get("next") or "post_detail", pk=pk)


@login_required
@require_POST
def toggle_like_ajax(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    liked = True
    if not created:
        like.delete()
        liked = False
    else:
        # уведомляем автора поста о новом лайке
        if post.author_id != request.user.id:
            try:
                Notification.objects.create(
                    to_user=post.author,
                    verb="like",
                    actor=request.user,
                    post_id=post.id,
                )
            except Exception:
                pass

    return JsonResponse({"liked": liked, "likes_count": post.likes.count()})


@login_required
@require_POST
def add_comment(request, pk):
    """
    Добавление корневого комментария.
    AJAX: JSON { rendered_html }, иначе — redirect.
    """
    post = get_object_or_404(Post, pk=pk)
    text = (request.POST.get("text") or "").strip()
    is_ajax = request.headers.get("X-Requested-With", "").lower() == "xmlhttprequest"

    if not text:
        if is_ajax:
            return JsonResponse({"error": "empty"}, status=400)
        return redirect("post_detail", pk=pk)

    c = Comment.objects.create(author=request.user, post=post, text=text)

    # уведомление автору поста (если коммент не свой)
    if post.author_id != request.user.id:
        try:
            Notification.objects.create(
                to_user=post.author, verb="comment", actor=request.user, post_id=post.id
            )
        except Exception:
            pass

    if is_ajax:
        html = render_to_string("partials/comment_item.html", {"c": c}, request=request)
        return JsonResponse({"rendered_html": html})

    next_url = request.POST.get("next") or reverse("post_detail", args=[pk])
    return redirect(next_url)


@login_required
def comment_edit(request, pk):
    comment = get_object_or_404(Comment, pk=pk, author=request.user)
    next_url = (
        request.GET.get("next")
        or request.POST.get("next")
        or reverse("post_detail", args=[comment.post_id])
    )

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, "Комментарий обновлён.")
            return redirect(next_url)
    else:
        form = CommentForm(instance=comment)

    return render(
        request,
        "comment_form.html",
        {"form": form, "title": "Редактировать комментарий", "next_url": next_url},
    )


@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk, author=request.user)
    post_pk = comment.post_id
    if request.method == "POST":
        comment.delete()
        messages.success(request, "Комментарий удалён.")
    return redirect(request.POST.get("next") or "post_detail", pk=post_pk)


@login_required
@require_POST
def add_reply(request, parent_id):
    """
    Добавление ответа на комментарий (1-й уровень).
    AJAX: JSON { rendered_html }, иначе — redirect.
    """
    parent = get_object_or_404(Comment, pk=parent_id)
    text = (request.POST.get("text") or "").strip()
    is_ajax = request.headers.get("X-Requested-With", "").lower() == "xmlhttprequest"

    if not text:
        if is_ajax:
            return JsonResponse({"error": "empty"}, status=400)
        return redirect("post_detail", pk=parent.post_id)

    r = Comment.objects.create(
        author=request.user, post=parent.post, parent=parent, text=text
    )

    # уведомление автору поста (если ответ не свой)
    if parent.post.author_id != request.user.id:
        try:
            Notification.objects.create(
                to_user=parent.post.author,
                verb="comment",
                actor=request.user,
                post_id=parent.post_id,
            )
        except Exception:
            pass

    if is_ajax:
        html = render_to_string("partials/comment_item.html", {"c": r}, request=request)
        return JsonResponse({"rendered_html": html})

    next_url = request.POST.get("next") or reverse(
        "post_detail", args=[parent.post_id]
    )
    return redirect(next_url)

