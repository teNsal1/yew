from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from .models import Application, News, NewsImage, UserProfile  # Добавлен импорт UserProfile
import bleach

ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'b', 'i', 'u', 's', 
    'ul', 'ol', 'li', 'a', 'img', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'blockquote', 'code', 'pre', 'hr', 'span', 'div'
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target'],
    'img': ['src', 'alt', 'width', 'height', 'style'],
    '*': ['class', 'style']
}


class RegistrationForm(UserCreationForm):
    """Форма регистрации нового пользователя"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'example@mail.com',
            'class': 'form-control'
        })
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Придумайте логин',
            'class': 'form-control'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Придумайте пароль',
            'class': 'form-control'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Повторите пароль',
            'class': 'form-control'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        """Проверка уникальности email"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует')
        return email


class MultipleFileInput(forms.ClearableFileInput):
    """Кастомный виджет для множественной загрузки файлов"""
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """Кастомное поле для множественной загрузки файлов"""
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        """Обработка множественных файлов"""
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class ApplicationForm(forms.ModelForm):
    """Форма для создания заявки на услугу (для пользователей)"""
    class Meta:
        model = Application
        fields = ['name', 'email', 'phone', 'service']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Введите ваше имя',
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'example@mail.com',
                'class': 'form-control'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': '+7 (___) ___-__-__',
                'class': 'form-control'
            }),
            'service': forms.Select(attrs={
                'class': 'form-control'
            }),
        }


class AdminApplicationForm(forms.ModelForm):
    """Форма для редактирования заявки администратором (включая статус)"""
    class Meta:
        model = Application
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'service': forms.Select(attrs={
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'created_at': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly'
            }),
        }


class NewsForm(forms.ModelForm):
    """Форма для создания и редактирования новостей с поддержкой множественных изображений"""
    images = MultipleFileField(
        label='Изображения',
        required=False,
        widget=MultipleFileInput(attrs={
            'class': 'form-control',
            'multiple': True
        })
    )

    class Meta:
        model = News
        fields = ['title', 'short_description', 'content']  # Добавлено short_description
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Краткое описание для списка новостей'}),
            'content': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 10,  # Увеличим высоту поля
                'id': 'news-content-editor'  # Добавляем ID для инициализации редактора
            }),
        }

    def clean_content(self):
        """Очистка HTML контента от потенциально опасных тегов"""
        content = self.cleaned_data.get('content')
        if content:
            cleaned_content = bleach.clean(
                content,
                tags=ALLOWED_TAGS,
                attributes=ALLOWED_ATTRIBUTES,
                strip=True
            )
            return cleaned_content
        return content

class ProfileEditForm(forms.ModelForm):
    """
    Форма для редактирования профиля пользователя.
    Включает базовые поля пользователя, телефон и функционал смены пароля.
    """
    
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': '+7 (___) ___-__-__',
            'class': 'form-control'
        }),
        label='Телефон',
        help_text='Необязательное поле для вашего контактного телефона'
    )
    
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Текущий пароль (для смены пароля)',
            'class': 'form-control'
        }),
        required=False,
        label='Текущий пароль',
        help_text='Введите текущий пароль только если хотите изменить пароль'
    )
    
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Новый пароль',
            'class': 'form-control'
        }),
        required=False,
        label='Новый пароль',
        help_text='Пароль должен содержать не менее 8 символов'
    )
    
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Повторите новый пароль',
            'class': 'form-control'
        }),
        required=False,
        label='Подтверждение пароля',
        help_text='Повторите новый пароль для подтверждения'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'phone']
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Введите ваш логин',
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'example@mail.com',
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        """
        Инициализация формы. Устанавливает начальное значение телефона из профиля пользователя.
        """
        super().__init__(*args, **kwargs)
        # Устанавливаем начальное значение телефона из профиля пользователя
        if hasattr(self.instance, 'profile'):
            self.fields['phone'].initial = self.instance.profile.phone

    def clean_email(self):
        """
        Проверяет уникальность email адреса исключая текущего пользователя.
        """
        email = self.cleaned_data.get('email')
        # Проверяем, что email уникален, исключая текущего пользователя
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует')
        return email

    def clean(self):
        """
        Валидация полей связанных с изменением пароля.
        Проверяет корректность ввода текущего пароля и совпадение новых паролей.
        """
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        current_password = cleaned_data.get('current_password')
        
        # Проверяем, если пользователь пытается изменить пароль
        if new_password1 or new_password2 or current_password:
            # Проверяем, что введен текущий пароль
            if not current_password:
                raise forms.ValidationError('Для смены пароля необходимо ввести текущий пароль')
            
            # Проверяем корректность текущего пароля
            if not self.instance.check_password(current_password):
                raise forms.ValidationError('Неверный текущий пароль')
            
            # Проверяем совпадение новых паролей
            if new_password1 != new_password2:
                raise forms.ValidationError('Новые пароли не совпадают')
            
            # Дополнительная проверка длины нового пароля
            if new_password1 and len(new_password1) < 8:
                raise forms.ValidationError('Новый пароль должен содержать не менее 8 символов')
        
        return cleaned_data

    def save(self, commit=True):
        """
        Сохраняет изменения профиля пользователя.
        Обновляет пароль если он был изменен и сохраняет телефон в профиль.
        
        Args:
            commit (bool): Флаг, указывающий нужно ли сохранять изменения в базу данных
            
        Returns:
            User: Обновленный объект пользователя
        """
        # Получаем объект пользователя без сохранения в базу
        user = super().save(commit=False)
        
        # Сохраняем телефон в профиль пользователя
        phone = self.cleaned_data.get('phone')
        if hasattr(user, 'profile'):
            user.profile.phone = phone
        else:
            # Создаем профиль, если его не существует
            UserProfile.objects.create(user=user, phone=phone)
        
        # Обновляем пароль, если он был изменен (после сохранения профиля)
        new_password = self.cleaned_data.get('new_password1')
        if new_password:
            user.set_password(new_password)
        
        if commit:
            # Сохраняем пользователя в базу данных
            user.save()
            # Сохраняем профиль пользователя, если он существует
            if hasattr(user, 'profile'):
                user.profile.save()
        
        return user