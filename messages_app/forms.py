from django import forms
from .models import Message
from django.contrib.auth import get_user_model

User = get_user_model()

class MessageForm(forms.ModelForm):
    recipient = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label="받는 사람",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Message
        fields = ['recipient', 'subject', 'content']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }