from django import forms



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