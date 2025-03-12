from django.urls import path
from .views import post_list, post_detail, post_create, post_update, post_delete, like_dislike_post, add_comment, like_dislike_comment, bookmark_toggle, bookmark_list

urlpatterns = [
    path("", post_list, name="post_list"),
    path("<int:post_id>/", post_detail, name="post_detail"),
    path("new/", post_create, name="post_create"),
    path("<int:post_id>/edit/", post_update, name="post_update"),
    path("<int:post_id>/delete/", post_delete, name="post_delete"),
    
    # 좋아요
    path("<int:post_id>/like/", like_dislike_post, name="like_dislike_post"),
    path("comment/<int:comment_id>/like/", like_dislike_comment, name="like_dislike_comment"),

    # 댓글
    path("<int:post_id>/comment/", add_comment, name="add_comment"),
    
    # 북마크
    path("<int:post_id>/bookmark/", bookmark_toggle, name="bookmark_toggle"),
    path("bookmarks/", bookmark_list, name="bookmark_list"),
    
]
