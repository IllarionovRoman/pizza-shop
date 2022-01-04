from django import forms
from .models import *
from django.core.exceptions import ValidationError


class ProductsForm(forms.ModelForm):
    image = forms.ImageField()

    class Meta:
        model = Products
        fields = [
            'name',
            'description',
            'price',
            'image',
            'categories',
            'slug'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = 'Название'
        self.fields['price'].label = 'Цена'
        self.fields['description'].label = 'Описание'
        self.fields['image'].label = 'Фотография'
        self.fields['categories'].label = 'Выберите категорию вашего продукта'
        self.fields['slug'].label = 'Слаг продукта'

    def clean_slug(self):
        new_slug = self.cleaned_data['slug'].lower()
        if new_slug == 'create':
            raise ValidationError('Категория с названием create не может быть создана')
        if Category.objects.filter(slug__iexact=new_slug).count():
            raise ValidationError('Данный id уже есть')
        return new_slug


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['title', 'slug']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = 'Название категории'
        self.fields['slug'].label = 'ID категории'

    def clean_slug(self):
        new_slug = self.cleaned_data['slug'].lower()
        if new_slug == 'create':
            raise ValidationError('Категория с названием create не может быть создана')
        if Category.objects.filter(slug__iexact=new_slug).count():
            raise ValidationError('Данная категория уже есть')
        return new_slug


class OrderForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Order
        fields = ('first_name', 'last_name', 'address', 'phone')


class LoginForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Логин'
        self.fields['password'].label = 'Пароль'

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        user = User.objects.filter(username=username).first()
        if not user:
            raise forms.ValidationError(f'Пользователь с логином {username} не найден')
        if not user.check_password(password):
            raise forms.ValidationError('Неверный пароль')
        return self.cleaned_data


class RegistrationForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Логин'
        self.fields['password'].label = 'Пароль'
        self.fields['confirm_password'].label = 'Подтвердите пароль'
        self.fields['first_name'].label = 'Имя'
        self.fields['last_name'].label = 'Фамилия'
        self.fields['email'].label = 'Электронная почта'

    def clean_email(self):
        email = self.cleaned_data['email']
        domain = email.split('.')[-1]
        if domain in ['com', 'net']:
            raise forms.ValidationError(f'Регистрация для домена {domain} невозможна')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Данная электронная почта уже занята')
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(f'Логин {username} занят')
        return username

    def clean(self):
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        if password != confirm_password:
            raise forms.ValidationError('Пароли не совпадают')
        return self.cleaned_data

    class Meta:
        model = User
        fields = [
            'username',
            'password',
            'confirm_password',
            'first_name',
            'last_name',
            'email',
        ]

