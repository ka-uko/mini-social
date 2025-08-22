from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('network.urls')),        # главная/лента
    path('accounts/', include('django.contrib.auth.urls')),# login/logout/password_change и т.п.
    path('accounts/', include('accounts.urls')), # signup
    path('messages/', include('messaging.urls')),#  сообщения
    path('notify/', include('notify.urls')), # уведомления
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)