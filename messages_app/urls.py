from django.urls import path
from . import views

app_name = 'messages'  # URL 네임스페이스

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('sent/', views.sent_messages, name='sent'),
    path('compose/', views.compose_message, name='compose'),
    path('view/<int:message_id>/', views.view_message, name='view'),
]