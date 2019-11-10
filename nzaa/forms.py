"""Forms for the NZAA archaeological site application.
"""

from django import forms
from django.forms import Form, ModelForm, widgets
from django.forms import Textarea, TextInput, NumberInput
from django.forms import CharField, ChoiceField, Select, HiddenInput
from django.forms import FileField, ModelChoiceField

import settings
import models 

WHAT_FIELDS = (
    ('site_type', 'Site type'),
    ('site_subtype', 'Subtype'),
    ('period', 'Period'),
    ('ethnicity', 'Ethnicity'),
)
WHERE_FIELDS = (
    ('location', 'Location'),
    ('region', 'Region'),
    ('tla', 'Territorial Authority'),
    ('island', 'Island'),
)

UPDATE_STATUS = (
    ('Pending', 'Pending'),
    ('Submitted', 'Submitted'),
    ('Returned', 'Returned'),
)


class BoundaryForm(ModelForm):
    class Meta:
        model = models.Boundary
        fields =  [
            'title',
            'client',
            'description',
            'notes',
            'rights',
            'comments',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows':2,'cols':40,}),
            'notes': forms.Textarea(attrs={'rows':2,'cols':40,}),
            'rights': forms.Textarea(attrs={'rows':2,'cols':40,}),
            'comments': forms.Textarea(attrs={'rows':2,'cols':40,}),
        }

class DocumentForm(ModelForm):
    class Meta:
        model= models.Document
        fields = [
            'doctype',
            'date',
            'author',
            'quality',
            'description',
        ]
        widgets = {
            'doctype': forms.Select(),
            'description': forms.Textarea(attrs={'rows': 2, 'cols': 40}),
        }

class SiteList(ModelForm):
    class Meta:
        model = models.SiteList
        fields = [
            'name',
            'long_name',
            'subject',
            'description',
            'notes',
            'list_type',
        ]
        widgets = {
            'subject': forms.Textarea(attrs={'rows': 2, 'cols': 40}),
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
            'notes': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }


# Legacy code, not checked.
class NewID(Form):
    """Collect the new nzaa identifier, assigned by Archsite.

    Validation: Reject if
        is empty
        is not a valid NZAA identifier
        points to an existing record

    """
    new_id = CharField(
        required=True,
    )

    def clean_new_id(self):
        new_id = self.cleaned_data['new_id']
        try:
            (sheet, ordinal) = new_id.split('/')
        except ValueError:
            raise forms.ValidationError(
                'NZAA id must be formatted as <sheet>/<number>.')

        if sheet not in settings.NZMS260:
            raise forms.ValidationError(
                'NZMS260 sheet identifier is not valid.')

        try:
            int(ordinal)
        except ValueError:
            raise forms.ValidationError(
                'There must be a number following the slash character.')

        try:
            s = models.Site.objects.get(nzaa_id=new_id)
            print s
            raise forms.ValidationError('This record exists already.')
        except models.Site.DoesNotExist:
            pass


class NewSiteForm(ModelForm):
    class Meta:
        model = models.NewSite
        fields = [
            'field_id',
            'field_notes',
            'update_type',
            'opstatus',
            'recorded_by',
            'recorded',
            'visited_by',
            'visited',
            'site_name',
            'other_name',
            'site_type',
            'site_subtype',
            'location',
            'easting',
            'northing',
            'period',
            'ethnicity',
            'landuse',
            'threats',
            'features',
            'associated_sites',
            'introduction',
            'finder_aid',
            'description',
            'condition',
            'references',
            'rights',
        ]

        widgets = {
            'introduction': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
            'finder_aid': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
            'description': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
            'condition': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
            'references': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
            'rights': forms.Textarea(attrs={'rows': 3, 'cols': 40}),

        }


# Legacy code, not checked.
class Search(Form):
    site_type = ModelChoiceField(
        queryset=models.Site.objects.order_by(
            'lgcy_type').distinct('lgcy_type'),
        to_field_name="site_type",
    )


# Legacy code, not checked.
class SelectUpdateStatus(Form):

    status = ChoiceField(
        label='Status',
        initial='Working',
        required=False,
        choices=UPDATE_STATUS,
    )
    opstatus = ChoiceField(
        label='Your status',
        initial='Working',
        required=False,
        choices=settings.get_choices(settings.OPSTATUS),
    )


class SimpleSearch(Form):
    terms = CharField(label='')


# Legacy code, not checked.
class SitePanel(ModelForm):
    class Meta:
        model = models.Site
        fields = [
            'easting',
            'northing',
            'location',
            'site_type',
            'site_subtype',
            'ethnicity',
            'period',
            'site_name',
            'other_name',
            'landuse',
            'threats',
            'features',
            'associated_sites',
            'visited',
            'visited_by',
        ]


class SiteReview(ModelForm):
    class Meta:
        model = models.Site
        fields = [
            'site_name',
            'other_name',
            'site_type',
            'site_subtype',
            'period',
            'ethnicity',
            'associated_sites',
            'features',
            'location',
            'easting',
            'northing',

            'recorded_by',
            'recorded',
            'updated_by',
            'updated',
            'visited_by',
            'visited',
            'record_quality',
        ]
        widgets = {
            'features': widgets.Textarea(
                attrs={'rows': 3, 'cols': 60, 'style': 'max-width: 100%;', }),
            'recorded_by': widgets.TextInput,
            'recorded': widgets.DateInput,
            'site_name': widgets.TextInput,
            'associated_sites': widgets.TextInput,
            'location': widgets.TextInput,
            'visited_by': widgets.TextInput,
            'visited': widgets.TextInput,
            'features': widgets.Textarea(attrs={'rows': 1, 'cols': 80, }),
        }


class UploadFile(Form):
    filename = FileField(required=False)

class UploadFile(Form):
    filename = FileField(required=False)

class UploadFileRequired(Form):
    filename = FileField(required=True)


class UpdateFull(ModelForm):
    class Meta:
        model = models.Update
        fields = [
            'update_type',
            'introduction',
            'finder_aid',
            'description',
            'condition',
            'references',
            'easting',
            'northing',
            'location',
            'site_type',
            'site_subtype',
            'ethnicity',
            'period',
            'features',
            'site_name',
            'other_name',
            'landuse',
            'threats',
            'associated_sites',
            'visited',
            'visited_by',
            'rights',
        ]


class UpdateMain(ModelForm):
    class Meta:
        model = models.Update
        fields = [
            'update_type',
            'introduction',
            'finder_aid',
            'description',
            'condition',
            'references',
            'rights',
        ]
        widgets = {
            'introduction': forms.Textarea(attrs={'rows': 5, 'cols': 80}),
            'finder_aid': forms.Textarea(attrs={'rows': 5, 'cols': 80}),
            'description': forms.Textarea(attrs={'rows': 5, 'cols': 80}),
            'condition': forms.Textarea(attrs={'rows': 5, 'cols': 80}),
            'references': forms.Textarea(attrs={'rows': 5, 'cols': 80}),
            'rights': forms.Textarea(attrs={'rows': 5, 'cols': 80}),
        }


class UpdatePanel(ModelForm):
    class Meta:
        model = models.Update
        fields = [
            'updated_by',
            'updated',
            'easting',
            'northing',
            'location',
            'site_type',
            'site_subtype',
            'ethnicity',
            'period',
            'features',
            'site_name',
            'other_name',
            'landuse',
            'threats',
            'associated_sites',
            'visited',
            'visited_by',
        ]
        widgets = {
            'updated_by': forms.TextInput(),

        }
