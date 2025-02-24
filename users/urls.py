from django.urls import path
from .views import signup, user_login, user_logout, home, profile, profile_edit, CustomPasswordChangeView, send_verification_email, verify_email_code, delete_user

urlpatterns = [
    path('', home, name='home'),
    path('signup/', signup, name='signup'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('profile/', profile, name='profile'),
    path('profile/edit/', profile_edit, name='profile_edit'),
    
    # 비밀번호 변경경
    path('password_change/', CustomPasswordChangeView.as_view(), name='password_change'),
    
    # 이메일 인증
    path('send_verification_email/', send_verification_email, name='send_verification_email'),
    path('verify_email_code/', verify_email_code, name='verify_email_code'),
    
    # 회원탈퇴
    path('delete_account/', delete_user, name='delete_user'),
]
