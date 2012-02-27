"""
Forms for auth
"""

from django import forms
from models import User
from django.utils.translation import ugettext_lazy as _

class RegisterForm(forms.ModelForm):
    email = forms.EmailField(_("Email"), required=True)

    class Meta:
        model = User
        fields = ('name', 'email')
