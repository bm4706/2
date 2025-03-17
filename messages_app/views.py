from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Message
from .forms import MessageForm

@login_required
def inbox(request):
    """받은 쪽지함 보기"""
    received_messages = Message.objects.filter(recipient=request.user)
    unread_count = received_messages.filter(is_read=False).count()
    
    return render(request, 'messages_app/inbox.html', {
        'messages_list': received_messages,
        'unread_count': unread_count
    })

@login_required
def sent_messages(request):
    """보낸 쪽지함 보기"""
    sent_messages = Message.objects.filter(sender=request.user)
    
    return render(request, 'messages_app/sent.html', {
        'messages_list': sent_messages
    })

@login_required
def compose_message(request):
    """새 쪽지 작성"""
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            messages.success(request, "쪽지를 성공적으로 전송했습니다.")
            return redirect('messages:sent')
    else:
        # URL 매개변수에서 수신자 정보를 가져올 수 있음
        recipient_id = request.GET.get('to')
        initial = {}
        if recipient_id:
            initial['recipient'] = recipient_id
        form = MessageForm(initial=initial)
    
    return render(request, 'messages_app/compose.html', {'form': form})

@login_required
def view_message(request, message_id):
    """쪽지 상세 보기"""
    message = get_object_or_404(Message, id=message_id)
    
    # 권한 확인 (받은 사람이나 보낸 사람만 볼 수 있음)
    if message.recipient != request.user and message.sender != request.user:
        messages.error(request, "이 쪽지에 접근할 권한이 없습니다.")
        return redirect('messages:inbox')
    
    # 받은 쪽지인 경우 읽음 상태로 변경
    if message.recipient == request.user and not message.is_read:
        message.is_read = True
        message.save()
    
    return render(request, 'messages_app/view.html', {'message': message})