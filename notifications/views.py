from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def notification_list(request):
    """알림 목록 보기"""
    notifications = Notification.objects.filter(recipient=request.user)
    unread_count = notifications.filter(is_read=False).count()
    
    return render(request, 'notifications/notification_list.html', {
        'notifications': notifications,
        'unread_count': unread_count
    })

@login_required
def mark_as_read(request, notification_id):
    """알림 읽음 표시"""
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    
    # 알림 클릭 시 해당 객체로 이동
    content_object = notification.content_object
    
    if notification.notification_type == Notification.LIKE or notification.notification_type == Notification.COMMENT:
        # 게시글이나 댓글 관련 알림
        if hasattr(content_object, 'post'):
            # 댓글인 경우 게시글로 이동
            return redirect('post_detail', post_id=content_object.post.id)
        else:
            # 게시글인 경우
            return redirect('post_detail', post_id=content_object.id)
    elif notification.notification_type == Notification.FOLLOW:
        # 팔로우 알림은 해당 사용자 프로필로 이동
        return redirect('profile')
    
    # 기본적으로 알림 목록으로 리디렉션
    return redirect('notifications:list')

@login_required
def mark_all_as_read(request):
    """모든 알림 읽음 표시"""
    if request.method == 'POST':
        notifications = Notification.objects.filter(recipient=request.user, is_read=False)
        notifications.update(is_read=True)
    
    return redirect('notifications:list')