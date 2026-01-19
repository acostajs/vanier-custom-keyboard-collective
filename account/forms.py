from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
            "address_line1",
            "address_line2",
            "city",
            "postal_code",
            "country",
        ]


class LoginForm(forms.Form):
    username = forms.CharField(label=_("username"))
    password = forms.CharField(label=_("password"), widget=forms.PasswordInput)
