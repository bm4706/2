from .models import Notification
from django.contrib.contenttypes.models import ContentType

def create_notification(recipient, actor, notification_type, content_object, text=None):
    """
    알림 생성 함수
    """
    # 자기 자신에게는 알림을 보내지 않음
    if recipient == actor:
        return None
        
    content_type = ContentType.objects.get_for_model(content_object)
    
    # 기본 텍스트 설정
    if text is None:
        if notification_type == Notification.LIKE:
            text = f"{actor.nickname}님이 회원님의 게시글을 좋아합니다."
        elif notification_type == Notification.COMMENT:
            text = f"{actor.nickname}님이 회원님의 게시글에 댓글을 남겼습니다."
        elif notification_type == Notification.FOLLOW:
            text = f"{actor.nickname}님이 회원님을 팔로우합니다."
        elif notification_type == Notification.MENTION:
            text = f"{actor.nickname}님이 회원님을 언급했습니다."
        elif notification_type == Notification.REPLY:
            text = f"{actor.nickname}님이 회원님의 댓글에 답글을 남겼습니다."
    
    notification = Notification.objects.create(
        recipient=recipient,
        actor=actor,
        notification_type=notification_type,
        content_type=content_type,
        object_id=content_object.id,
        text=text
    )
    
    return notification