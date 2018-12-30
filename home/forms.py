from django.forms import Form, ModelForm
from django.forms import Textarea, TextInput, CharField, Select
from django.forms import HiddenInput, PasswordInput, widgets, FileField

import settings
import members.models


class LoginForm(Form):
    username = CharField(label='Username')
    password = CharField(widget=PasswordInput)


class UploadFile(Form):
    filename = FileField(required=False)


class MemberForm(ModelForm):
    """User's member values."""

    class Meta:
        model = members.models.Member
        fields = [
            'initial',
            'nickname',
            'email',
            'phone',
        ]
