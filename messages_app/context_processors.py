def unread_messages_count(request):
    """읽지 않은 쪽지 수를 모든 템플릿에서 사용할 수 있게 합니다."""
    if request.user.is_authenticated:
        count = request.user.received_messages.filter(is_read=False).count()
        return {'unread_messages_count': count}
    return {'unread_messages_count': 0}