from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model() # 기존 사용자 모델 참조

class Post(models.Model):
    title = models.CharField(max_length=200)  # 게시글 제목
    content = models.TextField()  # 게시글 내용
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # 작성자 (사용자 연결)
    created_at = models.DateTimeField(auto_now_add=True)  # 작성일
    updated_at = models.DateTimeField(auto_now=True)  # 수정일

    def __str__(self):
        return self.title
