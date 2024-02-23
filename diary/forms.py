from django import forms
from .models import Data


class EditForm(forms.ModelForm):
    class Meta:
        model = Data
        fields = "__all__"
        widgets = {
            'posted_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M:00')
        }


class MailForm(forms.Form):
    sender = forms.EmailField(required=False,widget=forms.EmailInput(attrs={'placeholder': 'メールアドレスを入力してください(任意)'}))
    
    message = forms.CharField(
        required=True,
        max_length=1024,
        widget=forms.Textarea(
            attrs={
                'placeholder': '内容を1,024文字以内で入力してください。',
            }
        )
    )

    anonymas = forms.BooleanField(initial=True,required=False)
