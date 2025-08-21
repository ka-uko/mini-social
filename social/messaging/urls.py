from django.urls import path
from . import views

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('start/<str:username>/', views.start_thread, name='start_thread'),
    path('t/<int:pk>/', views.thread_detail, name='thread_detail'),
]
