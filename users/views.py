from django.shortcuts import render, redirect
from .forms import SignUpForm, LoginForm, ProfileEditForm
from .models import CustomUser
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth import authenticate, login, update_session_auth_hash, logout
from django.urls import reverse_lazy

from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.hashers import check_password

from posts.models import Post, Comment 
from django.contrib.auth.decorators import login_required

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

# 이메일 인증 코드 발송송
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





