from lugati.lugati_media.lugati_gallery.models import GalleryItem
from djangular.forms import NgFormValidationMixin, NgModelFormMixin,  NgModelForm
from django import forms
from djangular.styling.bootstrap3.forms import Bootstrap3Form, Bootstrap3FormMixin

from django.forms import Textarea, HiddenInput
from django.contrib.sites.models import get_current_site
class GalleryItemForm(NgModelForm):

    pic_array = forms.CharField(required=False, widget=HiddenInput)

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super(GalleryItemForm, self).__init__(*args, **kwargs)
        self.fields['site'].initial = get_current_site(request)

    class Meta:
        model = GalleryItem
        widgets = {
            'site': HiddenInput(),
        }

class NgGalleryItemForm(NgModelFormMixin, NgFormValidationMixin, GalleryItemForm, Bootstrap3FormMixin):
    form_name = "confirm_form"
    scope_prefix = 'submit_data'


