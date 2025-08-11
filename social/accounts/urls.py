from django.urls import path
from .views import SignupView
from . import views

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),

    # профиль и подписка
    path('u/<str:username>/', views.profile, name='profile'),
    path('<str:username>/', views.profile, name='profile_alias'),
    path('u/<str:username>/follow/', views.toggle_follow, name='toggle_follow'),
    path('u/<str:username>/followers/', views.followers_list, name='followers_list'),
    path('u/<str:username>/following/', views.following_list, name='following_list'),


]
