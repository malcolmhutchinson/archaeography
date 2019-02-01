"""Forms for the members application."""

from django import forms
from django.forms import Form, ModelForm, widgets
from django.forms import Textarea, TextInput, NumberInput
from django.forms import CharField, ChoiceField, Select, HiddenInput
from django.forms import FileField

import settings
import models

class BoundaryFileForm(ModelForm):
    class Meta:
        model = models.Boundary
        fields =  [
            'name',
            'client',
            'description',
            'notes',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows':2,'cols':40,}),
            'notes': forms.Textarea(attrs={'rows':2,'cols':40,}),
        }

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
class PersonDetails(ModelForm):
    class Meta:
        model = models.Person
        fields = [
            'name_first',
            'name_last',
        ]


class UploadFile(Form):
    filename = FileField(required=False)

