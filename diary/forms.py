from django import forms
from .models import Data

class EditForm(forms.ModelForm):
    class Meta:
        model = Data
        fields = "__all__"
