"""Forms for the members application."""

from django import forms
from django.forms import Form, ModelForm, widgets
from django.forms import Textarea, TextInput, NumberInput
from django.forms import CharField, ChoiceField, Select, HiddenInput
from django.forms import FileField

import settings
import models

class MemberDetails(ModelForm):
    class Meta:
        model = models.Member
        fields = [
            'nickname',
            'initial',
            'phone',
            'email',
            'affiliation',
            'interests',
        ]
        widgets = {
            'interests': widgets.Textarea(attrs={'rows': 3, 'cols': 20}),
        }


class MemberForm(ModelForm):
    """User's member values."""

    class Meta:
        model = models.Member
        fields = [
            'name',
            'initial',
            'nickname',
            'email',
            'phone',
        ]

class UploadFile(Form):
    filename = FileField(required=False)

