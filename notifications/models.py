from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = get_user_model()

class Notification(models.Model):
    # 알림 유형
    LIKE = 'like'
    COMMENT = 'comment'
    FOLLOW = 'follow'
    MENTION = 'mention'
    REPLY = 'reply'
    
    NOTIFICATION_TYPES = (
        (LIKE, '좋아요'),
        (COMMENT, '댓글'),
        (FOLLOW, '팔로우'),
        (MENTION, '멘션'),
        (REPLY, '답글'),
    )
    
    # 알림 받는 사용자
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    
    # 알림 보낸 사용자
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actions')
    
    # 알림 유형
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    
    # 알림 관련 객체 (게시글, 댓글 등)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # 알림 텍스트
    text = models.CharField(max_length=255)
    
    # 읽음 여부
    is_read = models.BooleanField(default=False)
    
    # 생성 시간
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.actor} {self.get_notification_type_display()} to {self.recipient}"