from django import forms
from .models import CustomUser

class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(label="비밀번호", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="비밀번호 확인", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = CustomUser
        fields = ('email', 'nickname')

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("비밀번호가 일치하지 않습니다.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])  # 비밀번호 암호화
        if commit:
            user.save()
        return user



class LoginForm(forms.Form):
    email = forms.EmailField(label="이메일", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="비밀번호", widget=forms.PasswordInput(attrs={'class': 'form-control'}))



class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['nickname', 'profile_image']  # 프로필 이미지 포함
        widgets = {
            'nickname': forms.TextInput(attrs={'class': 'form-control'}),
        }



# 비밀번호 재설정 폼
class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="이메일")
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if not CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("해당 이메일로 등록된 계정이 존재하지 않습니다.")
        return email

class SetNewPasswordForm(forms.Form):
    password1 = forms.CharField(label="새 비밀번호", widget=forms.PasswordInput())
    password2 = forms.CharField(label="새 비밀번호 확인", widget=forms.PasswordInput())
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("비밀번호가 일치하지 않습니다.")

        return cleaned_data