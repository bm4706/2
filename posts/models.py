from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from taggit.managers import TaggableManager

User = get_user_model() # 기존 사용자 모델 참조

class Post(models.Model):
    title = models.CharField(max_length=200)  # 게시글 제목
    content = models.TextField()  # 게시글 내용
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # 작성자 (사용자 연결)
    created_at = models.DateTimeField(auto_now_add=True)  # 작성일
    updated_at = models.DateTimeField(auto_now=True)  # 수정일
    # 이미지 추가
    image = models.ImageField(upload_to='post_image',blank=True, null=True)
    
    # 태그 필드 추가
    tags = TaggableManager(blank=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    """댓글 모델"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author} - {self.post.title[:10]}"


class LikeDislike(models.Model):
    """게시글 & 댓글 공통 좋아요/싫어요 모델"""
    LIKE = 1
    DISLIKE = -1

    CHOICES = (
        (LIKE, "좋아요"),
        (DISLIKE, "싫어요"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)  # 게시글 또는 댓글 구분
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")  # 동적으로 연결
    
    value = models.SmallIntegerField(choices=CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "content_type", "object_id")  # 한 사용자가 하나의 게시글 또는 댓글에 한 번만 가능

    def __str__(self):
        return f"{self.user} ({'좋아요' if self.value == 1 else '싫어요'}) - {self.content_object}"

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'post')  # 한 사용자가 같은 게시글을 중복 북마크하지 못하도록
        
    def __str__(self):
        return f"{self.user.nickname}의 북마크: {self.post.title}"
    