from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # посты
    path('post/create/', views.post_create, name='post_create'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('post/<int:pk>/delete/', views.post_delete, name='post_delete'),

    # лайки и комментарии
    path('post/<int:pk>/like/', views.toggle_like, name='toggle_like'),
    path('post/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:pk>/edit/', views.comment_edit, name='comment_edit'),
    path('comment/<int:pk>/delete/', views.comment_delete, name='comment_delete'),
    path('comment/<int:parent_id>/reply/', views.add_reply, name='add_reply'),
    path('post/<int:pk>/like-ajax/', views.toggle_like_ajax, name='toggle_like_ajax'),
    # поиск
    path('search/', views.search, name='search'),

]
