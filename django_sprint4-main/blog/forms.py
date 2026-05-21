from django import forms
from django.contrib.auth.models import User

from blog.models import Post, Comment, Category, Location


class PostForm(forms.ModelForm):
    """Форма для создания и редактирования поста."""
    
    class Meta:
        model = Post
        fields = ['title', 'text', 'pub_date', 'category', 'location', 'image', 'is_published']
        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            ),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите заголовок'
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Введите текст публикации'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_published': forms.HiddenInput(),  
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(is_published=True)
        self.fields['location'].queryset = Location.objects.filter(is_published=True)
        self.fields['location'].empty_label = 'Не выбрано'
        self.fields['location'].required = False
        
        self.fields['is_published'].initial = True
        self.fields['is_published'].required = False


class ProfileForm(forms.ModelForm):
    """Форма для редактирования профиля пользователя."""
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class CommentForm(forms.ModelForm):
    """Форма для создания комментария."""
    
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Напишите ваш комментарий...'
            }),
        }
