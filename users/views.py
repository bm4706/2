from django.shortcuts import get_object_or_404, render, redirect
from .forms import SignUpForm, LoginForm, ProfileEditForm
from .models import CustomUser, Follow
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth import authenticate, login, update_session_auth_hash, logout
from django.urls import reverse_lazy

from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.hashers import check_password

from posts.models import Post, Comment
from django.contrib.auth.decorators import login_required

from .forms import PasswordResetRequestForm, SetNewPasswordForm # 비밀번호 재설정정
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # 회원가입 후 로그인 페이지로 이동
    else:
        form = SignUpForm()

    return render(request, "users/signup.html", {"form": form})


def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = authenticate(request, email=email, password=password)  # Django 기본 인증 사용
            if user is not None:
                login(request, user)  # Django 로그인 함수 사용
                return redirect('profile')
            else:
                form.add_error(None, "이메일 또는 비밀번호가 잘못되었습니다.")
    else:
        form = LoginForm()

    return render(request, "users/login.html", {"form": form})

def user_logout(request):
    logout(request)  # Django 기본 logout 함수 사용
    return redirect('login')  # 로그아웃 후 로그인 페이지로 이동

def home(request):
    return render(request, "users/home.html")


def profile(request):
    """
    1. 사용자 정보
    2. 내가 작성한 게시글과 댓글 확인
    """
    if not request.user.is_authenticated:  
        return redirect('login')  # 로그인하지 않은 경우 로그인 페이지로 이동
    
    user = request.user 
    
    # 게시글과 댓글 가져오기
    my_posts = Post.objects.filter(author=user).order_by("-created_at")
    my_comments = Comment.objects.filter(author=user).order_by("-created_at")
    
    return render(request, "users/profile.html", {
        "user": user,
        "my_posts": my_posts,
        "my_comments": my_comments
    })

def profile_edit(request):
    if not request.user.is_authenticated:
        return redirect('login')

    user = request.user  # Django 기본 인증 시스템 사용

    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=user)  # `request.FILES` 추가
        if form.is_valid():
            form.save()
            return redirect('profile')  # 수정 후 프로필 페이지로 이동
    else:
        form = ProfileEditForm(instance=user)

    return render(request, "users/profile_edit.html", {"form": form, "user": user})




class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'users/password_change.html'
    success_url = reverse_lazy('profile')

    def dispatch(self, request, *args, **kwargs):
        # Django 기본 인증 시스템을 사용하여 로그인 여부 확인
        if not request.user.is_authenticated:
            return redirect('login')  # 로그인하지 않은 경우 로그인 페이지로 이동

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        
        # 비밀번호 변경 후 세션 정보 업데이트
        user = form.user
        update_session_auth_hash(self.request, user)  # 세션 유지
        return response

# 이메일 인증 코드 발송
def send_verification_email(request):
    """이메일 인증 코드 생성 및 발송"""
    user = request.user
    if not user.is_authenticated:
        return redirect('login')

    user.generate_verification_code()  # 인증 코드 생성 후 저장

    send_mail(
        subject="이메일 인증 코드",
        message=f"안녕하세요 {user.nickname}님,\n\n이메일 인증 코드: {user.email_verification_code}\n\n이 코드를 입력하여 이메일을 인증하세요.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

    messages.success(request, "이메일이 성공적으로 발송되었습니다!")  # 메시지 추가
    return redirect('profile')  # 이메일을 보낸 후 프로필 페이지로 이동



# 이메일 인증 코드
def verify_email_code(request):
    """ 
    1) 사용자가 입력한 코드와 db에 저장된 인증 코드를 비교하여 검증
    2) 인증 성공시 True로 변경
    3) 인증 후 코드를 삭제해서 재사용 방지지

    """
    if request.method == "POST":
        input_code = request.POST.get("verification_code")  # 사용자가 입력한 코드
        user = request.user

        if user.email_verification_code == input_code:  # 코드 비교
            user.is_email_verified = True  # 인증 완료 처리
            user.email_verification_code = None  # 인증 후 코드 삭제
            user.save()
            return HttpResponse("이메일 인증이 완료되었습니다!")
        else:
            return HttpResponse("잘못된 인증 코드입니다. 다시 시도하세요.")

    return render(request, "users/verify_email.html")


# 회원 탈퇴 기능
def delete_user(request):
    """
    1) 사용자가 입력한 비밀번호가 현재 비밀번호와 일치 여부 확인
    2) 일치한다면 user.delete()로 계정 삭제후 로그아웃
    3) 불일치시 오류메세지 출력력
    """
    if request.method == "POST":
        password = request.POST.get("password")
        user = request.user

        # 비밀번호 확인
        if check_password(password, user.password):  
            user.delete()  # 회원 삭제
            logout(request)  # 세션 초기화 (자동 로그아웃)
            messages.success(request, "회원 탈퇴가 완료되었습니다.")
            return redirect("login")  # 로그인 페이지로 이동
        else:
            messages.error(request, "비밀번호가 일치하지 않습니다.")

    return render(request, "users/delete_user.html")



def password_reset_request(request):
    """비밀번호 재설정 요청 처리"""
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            user = CustomUser.objects.get(email=email)
            
            # 토큰 생성
            token = user.generate_password_reset_token()
            
            # 안전한 URL 생성용 사용자 ID 인코딩
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            
            # 비밀번호 재설정 링크 생성
            reset_url = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})
            )
            
            # 이메일 발송
            send_mail(
                subject="비밀번호 재설정 안내",
                message=f"""안녕하세요, {user.nickname}님.
                
비밀번호 재설정을 요청하셨습니다. 아래 링크를 클릭하여 새 비밀번호를 설정하세요:

{reset_url}

이 링크는 24시간 동안만 유효합니다.
요청하지 않으셨다면 이 이메일을 무시하셔도 됩니다.""",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            
            messages.success(request, "비밀번호 재설정 링크가 이메일로 발송되었습니다.")
            return redirect('login')
    else:
        form = PasswordResetRequestForm()
    
    return render(request, "users/password_reset_request.html", {"form": form})

def password_reset_confirm(request, uidb64, token):
    """비밀번호 재설정 링크 확인 및 새 비밀번호 설정"""
    try:
        # 사용자 ID 디코딩
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
    
    # 사용자와 토큰 유효성 검사
    if user is None or not user.is_password_reset_token_valid(token):
        messages.error(request, "비밀번호 재설정 링크가 유효하지 않습니다.")
        return redirect('password_reset_request')
    
    if request.method == "POST":
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            # 새 비밀번호 설정
            user.set_password(form.cleaned_data["password1"])
            
            # 토큰 무효화
            user.password_reset_token = None
            user.password_reset_token_created_at = None
            user.save()
            
            messages.success(request, "비밀번호가 성공적으로 변경되었습니다. 새 비밀번호로 로그인하세요.")
            return redirect('password_reset_complete')
    else:
        form = SetNewPasswordForm()
    
    return render(request, "users/password_reset_confirm.html", {"form": form})

def password_reset_complete(request):
    """비밀번호 재설정 완료 페이지"""
    return render(request, "users/password_reset_complete.html")



@login_required
def follow_toggle(request, user_id):
    """사용자 팔로우/언팔로우 토글 기능"""
    if request.method != 'POST':
        return redirect('profile')
        
    target_user = get_object_or_404(CustomUser, id=user_id)
    
    # 자기 자신을 팔로우할 수 없음
    if request.user == target_user:
        messages.error(request, '자기 자신을 팔로우할 수 없습니다.')
        return redirect('profile')
    
    # 이미 팔로우 중인지 확인
    follow_relation = Follow.objects.filter(follower=request.user, following=target_user)
    
    if follow_relation.exists():
        # 팔로우 관계가 있으면 삭제 (언팔로우)
        follow_relation.delete()
        messages.success(request, f'{target_user.nickname}님 팔로우를 취소했습니다.')
    else:
        # 팔로우 관계가 없으면 생성 (팔로우)
        Follow.objects.create(follower=request.user, following=target_user)
        messages.success(request, f'{target_user.nickname}님을 팔로우합니다.')
    
    # 이전 페이지로 리디렉션
    return redirect(request.META.get('HTTP_REFERER', 'profile'))

@login_required
def followers_list(request, nickname=None):
    """팔로워 목록 보기 (나를 팔로우하는 사람들)"""
    if nickname:
        user = get_object_or_404(CustomUser, nickname=nickname)
    else:
        user = request.user
    
    # 사용자의 팔로워 목록 가져오기
    followers = user.followers.all().select_related('follower')
    
    # 각 팔로워에 대해 현재 사용자가 팔로우하는지 여부 계산
    followers_data = []
    for follow in followers:
        follower = follow.follower
        is_following = Follow.objects.filter(follower=request.user, following=follower).exists() if request.user.is_authenticated else False
        followers_data.append({
            'user': follower,
            'is_following': is_following
        })
    
    context = {
        'user': user,
        'followers_data': followers_data,
        'is_self': user == request.user,
    }
    
    return render(request, 'users/followers_list.html', context)
@login_required
def following_list(request, nickname=None):
    """팔로잉 목록 가져오기"""
    if nickname:
        user = get_object_or_404(CustomUser, nickname=nickname)
    else:
        user = request.user
    
    # 사용자가 팔로우하는 목록 가져오기
    following = user.following.all().select_related('following')
    following_list = [follow.following for follow in following]
    
    context = {
        'user': user,
        'following': following_list,
        'is_self': user == request.user,
    }
    
    return render(request, 'users/following_list.html', context)