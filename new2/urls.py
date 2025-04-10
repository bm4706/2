from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),  # 홈 페이지 포함
    path('posts/', include("posts.urls")),
    path('messages/', include('messages_app.urls')),
    path('notifications/', include('notifications.urls',namespace='notifications'))
]


# 미디어 파일 제공 설정 (개발 환경)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)