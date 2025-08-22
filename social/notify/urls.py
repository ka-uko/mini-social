from django.urls import path
from . import views

urlpatterns = [
    path('', views.inbox, name='notify_inbox'),
    path('read/<int:pk>/', views.mark_read, name='notify_read'),
]