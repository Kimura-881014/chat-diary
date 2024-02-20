from django import forms
from django.contrib.auth.hashers import make_password
from django.forms import ModelForm, PasswordInput
from django.contrib.auth.forms import SetPasswordForm
from .models import ChatType
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class ChatTypeForm(ModelForm):
    class Meta:
        model = ChatType
        fields = '__all__'
        widgets = {
            'password': PasswordInput(),
        }

    def clean_password(self):
        # パスワードをハッシュ化して返す
        raw_password = self.cleaned_data.get('password')
        return make_password(raw_password)



class SetPasswordForm(forms.Form):
    """
    A form that lets a user change set their password without entering the old
    password
    """
 
    error_messages = {
        "password_mismatch": _("The two password fields didn't match."),
    }
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", 'class': 'form-control'}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", 'class': 'form-control'}),
    )
 
    def __init__(self, index, *args, **kwargs):
        self.index = index
        super().__init__(*args, **kwargs)
 
    def clean_new_password2(self):
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")
        if password1 and password2:
            if password1 != password2:
                raise ValidationError(
                    self.error_messages["password_mismatch"],
                    code="password_mismatch",
                )
        # password_validation.validate_password(password2, self.user)
        return password2
 