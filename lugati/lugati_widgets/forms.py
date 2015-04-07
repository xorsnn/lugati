# -*- coding: utf-8 -*-
from django import forms
from .models import LugatiTextBlock, LugatiNews, LugatiPoem
from django.forms import Textarea, HiddenInput
from django.utils.translation import ugettext as _
from djangular.forms import NgFormValidationMixin, NgModelFormMixin, NgModelForm
from djangular.styling.bootstrap3.forms import Bootstrap3Form, Bootstrap3FormMixin
from django.conf import settings
from lugati.products.models import Brand
from lugati.lugati_widgets.models import LugatiPortfolioItem

class LugatiTextBlockForm(NgModelForm):

    class Meta:
        model = LugatiTextBlock
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'ckeditor': 'editorOptions', 'ng-model': 'submit_data.text'}),
        }

class NgLugatiTextBlockForm(NgModelFormMixin, NgFormValidationMixin, LugatiTextBlockForm, Bootstrap3FormMixin):
    form_name = "confirm_form"
    scope_prefix = 'submit_data'

class LugatiNewsForm(NgModelForm):

    class Meta:
        model = LugatiNews
        widgets = {
            # 'name': forms.TextInput(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'ckeditor': 'editorOptions', 'ng-model': 'submit_data.description'}),
            'site': forms.HiddenInput()
        }

class NgLugatiNewsForm(NgModelFormMixin, NgFormValidationMixin, LugatiNewsForm, Bootstrap3FormMixin):
    form_name = "confirm_form"
    scope_prefix = 'submit_data'

class LugatiPoemForm(NgModelForm):
    pic_array = forms.CharField(required=False, widget=HiddenInput)
    class Meta:
        model = LugatiPoem
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'ckeditor': 'editorOptions', 'ng-model': 'submit_data.description'}),
        }

class NgLugatiPoemForm(NgModelFormMixin, NgFormValidationMixin, LugatiPoemForm, Bootstrap3FormMixin):
    form_name = "confirm_form"
    scope_prefix = 'submit_data'

class LugatiPortfolioItemForm(NgModelForm):
    pic_array = forms.CharField(required=False, widget=HiddenInput)
    class Meta:
        model = LugatiPortfolioItem
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'ckeditor': 'editorOptions', 'ng-model': 'submit_data.description'}),
        }

class NgLugatiPortfolioItemForm(NgModelFormMixin, NgFormValidationMixin, LugatiPortfolioItemForm, Bootstrap3FormMixin):
    form_name = "confirm_form"
    scope_prefix = 'submit_data'
