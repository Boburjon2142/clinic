from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import User, Roles


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(label="Ism", required=False,
                                 widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Ismingiz"}))
    last_name = forms.CharField(label="Familiya", required=False,
                                widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Familiyangiz"}))
    email = forms.EmailField(label="Email", required=False,
                             widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "email@misol.uz"}))

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Foydalanuvchi nomi"}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        # Default role for self-registered users
        if not user.role:
            user.role = "staff"
        if commit:
            user.save()
        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Style password fields from UserCreationForm
        if 'password1' in self.fields:
            self.fields['password1'].widget.attrs.update({"class": "form-control", "placeholder": "Parol"})
        if 'password2' in self.fields:
            self.fields['password2'].widget.attrs.update({"class": "form-control", "placeholder": "Parolni tasdiqlang"})


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Foydalanuvchi nomi",
                               widget=forms.TextInput(attrs={"autofocus": True, "class": "form-control", "placeholder": "Foydalanuvchi nomi"}))
    password = forms.CharField(label="Parol",
                               widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Parol"}))


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "avatar")
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "avatar": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}),
        }


class AdminCreateUserForm(UserCreationForm):
    first_name = forms.CharField(label="Ism", required=False,
                                 widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(label="Familiya", required=False,
                                widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.EmailField(label="Email", required=False,
                             widget=forms.EmailInput(attrs={"class": "form-control"}))
    role = forms.ChoiceField(label="Rol", choices=Roles.choices,
                             widget=forms.Select(attrs={"class": "form-select"}))

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "role")
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Style password fields
        if 'password1' in self.fields:
            self.fields['password1'].widget.attrs.update({"class": "form-control"})
        if 'password2' in self.fields:
            self.fields['password2'].widget.attrs.update({"class": "form-control"})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data.get('role') or user.role
        if user.role in (Roles.ADMIN, Roles.ADMIN1, Roles.ADMIN2, Roles.ADMIN3):
            user.is_staff = True
        if commit:
            user.save()
        return user
