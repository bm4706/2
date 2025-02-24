from django.urls import path
from .views import post_list, post_detail, post_create, post_update, post_delete

urlpatterns = [
    path("", post_list, name="post_list"),
    path("<int:post_id>/", post_detail, name="post_detail"),
    path("new/", post_create, name="post_create"),
    path("<int:post_id>/edit/", post_update, name="post_update"),
    path("<int:post_id>/delete/", post_delete, name="post_delete"),
]
