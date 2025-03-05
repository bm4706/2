from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
import string, datetime, secrets
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, email, nickname, password=None):
        if not email:
            raise ValueError("이메일은 필수입니다.")
        user = self.model(email=self.normalize_email(email), nickname=nickname)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nickname, password):
        user = self.create_user(email, nickname, password)
        user.is_admin = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser):
    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=30, unique=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)  # 프로필 이미지 추가
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)  # 이메일 인증 여부
    email_verification_code = models.CharField(max_length=6, blank=True, null=True) # 인증 코드 저장
    
    # 비밀번호 재설정
    password_reset_token = models.CharField(max_length=100, blank=True, null=True)
    password_reset_token_created_at = models.DateTimeField(blank=True, null=True)
    
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname']

    def __str__(self):
        return self.nickname

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def is_authenticated(self):
        """Django의 기본 인증 시스템과 호환되도록 is_authenticated 추가"""
        return True
    
    def generate_verification_code(self):
        """6자리 랜덤 인증 코드 생성"""
        digit_and_alpha = string.ascii_letters + string.digits
        self.email_verification_code = "".join(secrets.choice(digit_and_alpha) for _ in range(6))
        self.save()

    def generate_password_reset_token(self):
        
        chars = string.ascii_letters + string.digits
        token = ''.join(secrets.choice(chars) for _ in range(50))
        
        self.password_reset_token = token
        self.password_reset_token_created_at = timezone.now()
        self.save(update_fields=['password_reset_token', 'password_reset_token_created_at'])
        
        return token
    
    
    def is_password_reset_token_valid(self, token):
        if self.password_reset_token != token:
            return False
            
        if self.password_reset_token_created_at is None:
            return False
            
        # 토큰 만료 확인 (24시간)
        expiry_time = self.password_reset_token_created_at + datetime.timedelta(hours=24)
        return timezone.now() <= expiry_time
    
    
    
class Follow(models.Model):
    follower = models.ForeignKey(CustomUser, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(CustomUser, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('follower', 'following')  # 중복 팔로우 방지
        
    def __str__(self):
        return f"{self.follower.nickname} follows {self.following.nickname}"