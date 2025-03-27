from django import forms
from .models import Post,Comment


# 검색 폼폼    
class PostSearchForm(forms.Form):
    query = forms.CharField(label='검색어', required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '제목, 내용, 작성자 검색'}))
    search_type = forms.ChoiceField(
        label='검색 유형',
        required=False,
        choices=[
            ('all', '전체'),
            ('title', '제목'),
            ('content', '내용'),
            ('author', '작성자'),
            
        ],
        initial='all',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    
    
# 글 작성 폼
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image','tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '쉼표(,)로 구분하여 입력하세요'}),
        }
        
        
# 댓글 폼
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': '댓글을 입력하세요'}),
        }