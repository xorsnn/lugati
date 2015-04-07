from lugati.lugati_media.models import ThebloqVideo
from djangular.forms import NgFormValidationMixin, NgModelFormMixin
from django import forms

from django.forms import Textarea, HiddenInput

class ThebloqVideoForm(forms.ModelForm):
    class Meta:
        model = ThebloqVideo
        widgets = {
            'site': HiddenInput(),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'video_id': forms.TextInput(attrs={'class': 'form-control'}),
            'vimeo_id': forms.TextInput(attrs={'class': 'form-control'}),
            'video_code': forms.Textarea(attrs={'class': 'form-control'})
        }

class NgThebloqVideoForm(NgModelFormMixin, NgFormValidationMixin, ThebloqVideoForm):
    form_name = "confirm_form"
    scope_prefix = 'submit_data'


