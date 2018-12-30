"""Forms for the geodata library."""

from django import forms
from django.forms import Form, ModelForm, widgets
from django.forms import Textarea, TextInput, NumberInput
from django.forms import CharField, ChoiceField, Select, HiddenInput
from django.forms import FileField

import settings
import models


class SimpleSearch(Form):
    terms = CharField(label='')


class AerialSurveyForm(ModelForm):

    class Meta:
        model = models.AerialSurvey
        fields = (
            'name',
            'year_first',
            'year_last',
            'film_type',
            'rights',
            'comments',
        )


class AerialRunForm(ModelForm):

    class Meta:
        model = models.AerialRun
        fields = (
            'direction',
        )


class AerialFrameForm(ModelForm):

    class Meta:
        model = models.AerialFrame
        fields = (
            'coverage',
            'date_flown',
            'time_flown',
            'alt_ft',
            'aperture',
            'status',
            'name',
            'description',
            'georef_notes',
            'provenance',
            'rights',
        )


class AerialNewSurveyForm(ModelForm):
    class Meta:
        model = models.AerialSurvey
        fields = (
            'identifier',
            'name',
            'year_first',
            'year_last',
            'film_type',
            'rights',
            'comments',
        )


class AerialNewFrameForm(ModelForm):
    class Meta:
        model = models.AerialFrame
        fields = (
            'identifier',
            'coverage',
            'date_flown',
            'status',
        )
