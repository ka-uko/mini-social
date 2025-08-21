from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import Post, Like, Comment
from .forms import PostForm, CommentForm

from accounts.models import Follow



def home(request):
    feed = request.GET.get('feed')  # None | 'sub'

    if request.user.is_authenticated and feed == 'sub':
        following_ids = Follow.objects.filter(
            follower=request.user
        ).values_list('following_id', flat=True)

        posts = (Post.objects
                 .filter(author_id__in=following_ids)
                 .select_related('author')
                 .prefetch_related('likes', 'comments__author'))
    else:
        posts = (Post.objects
                 .select_related('author')
                 .prefetch_related('likes', 'comments__author'))

    form = PostForm() if request.user.is_authenticated else None
    return render(request, 'home.html', {'posts': posts, 'form': form, 'feed': feed})


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Пост создан.')
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'post_form.html', {'form': form, 'title': 'Новый пост'})


def post_detail(request, pk):
    post = get_object_or_404(Post.objects.select_related('author'), pk=pk)
    comments = (
        post.comments
            .select_related('author', 'parent')
            .prefetch_related('replies__author', 'replies__replies__author')  # глубже на уровень
            .all()
    )
    comment_form = CommentForm() if request.user.is_authenticated else None
    user_liked = request.user.is_authenticated and post.likes.filter(user=request.user).exists()
    return render(request, 'post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'user_liked': user_liked,
    })

@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Пост обновлён.')
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'post_form.html', {'form': form, 'title': 'Редактировать пост'})


@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Пост удалён.')
        return redirect('home')
    return render(request, 'post_confirm_delete.html', {'post': post})


@require_POST
@login_required
def toggle_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
        messages.info(request, 'Лайк убран.')
    else:
        messages.success(request, 'Пост понравился.')
    return redirect(request.POST.get('next') or 'post_detail', pk=pk)


@require_POST
@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        messages.success(request, 'Комментарий добавлен.')
    return redirect(request.POST.get('next') or 'post_detail', pk=pk)


@login_required
def comment_edit(request, pk):
    comment = get_object_or_404(Comment, pk=pk, author=request.user)
    next_url = request.GET.get('next') or request.POST.get('next') or reverse('post_detail', args=[comment.post_id])

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Комментарий обновлён.')
            return redirect(next_url)
    else:
        form = CommentForm(instance=comment)

    return render(request, 'comment_form.html', {
        'form': form,
        'title': 'Редактировать комментарий',
        'next_url': next_url,
    })


@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk, author=request.user)
    post_pk = comment.post_id
    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Комментарий удалён.')
    return redirect(request.POST.get('next') or 'post_detail', pk=post_pk)


@require_POST
@login_required
def add_reply(request, parent_id):
    parent = get_object_or_404(Comment.objects.select_related('post'), pk=parent_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        reply = form.save(commit=False)
        reply.author = request.user
        reply.post = parent.post           # тот же пост
        reply.parent = parent              # родительский комментарий
        reply.save()
        messages.success(request, 'Ответ добавлен.')
    return redirect(request.POST.get('next') or 'post_detail', pk=parent.post_id)