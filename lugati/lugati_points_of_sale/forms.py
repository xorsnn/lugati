# -*- coding: utf-8 -*-

from .models import SalesPoint, City
from django import forms
from django.forms import Textarea, HiddenInput
from django.utils.translation import ugettext as _
from lugati.products.models import Product
from djangular.forms import NgFormValidationMixin, NgModelFormMixin
from django.contrib.sites.models import Site
from djangular.forms import NgFormValidationMixin, NgModelFormMixin, NgModelForm
from djangular.styling.bootstrap3.forms import Bootstrap3Form, Bootstrap3FormMixin

class PosForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        cur_site = kwargs.pop('site')
        super(PosForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            cur_site = kwargs['instance'].site
            self.fields['product'] = forms.ModelChoiceField(queryset=Product.objects.filter(site=cur_site).filter(is_category=False),
                                                                     widget=forms.Select(attrs={'class':'form-control'}),
                                                                     required=False,
                                                                     label=_(u'Товар'))
            self.fields['city'] = forms.ModelChoiceField(queryset=City.objects.filter(site=cur_site),
                                                                     widget=forms.Select(attrs={'class':'form-control'}),
                                                                     required=False,
                                                                     label=_(u'Регион'))
        else:

            self.fields['product'] = forms.ModelChoiceField(queryset=Product.objects.filter(site=cur_site).filter(is_category=False),
                                                                     widget=forms.Select(attrs={'class':'form-control'}),
                                                                     required=False,
                                                                     label=_(u'Товар'))
            self.fields['city'] = forms.ModelChoiceField(queryset=City.objects.filter(site=cur_site),
                                                                     widget=forms.Select(attrs={'class':'form-control'}),
                                                                     required=False,
                                                                     label=_(u'Регион'))


    class Meta:
        model = SalesPoint
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'link': forms.TextInput(attrs={'class': 'form-control'}),



            'lng': forms.TextInput(attrs={'class': 'form-control'}),
            'lat': forms.TextInput(attrs={'class': 'form-control'}),
            'shop': HiddenInput(),
            'site': HiddenInput()
        }

class NgPosForm(NgModelFormMixin, NgFormValidationMixin, PosForm):
    form_name = 'submit_data_form'
    scope_prefix = 'submit_data'

#class CityForm(forms.ModelForm):
#    class Meta:
#        model = City
#        widgets = {
#        #    'lng': HiddenInput(),
#        #    'lat': HiddenInput(),
#            'site': HiddenInput()
#        }
class CityForm(NgModelForm):
    class Meta:
        model = City
        # exclude = ('site')
        widgets = {
            'site': HiddenInput(),
            # 'is_region':forms.CheckboxInput(attrs={'class': 'form-control'}),
            # 'name':forms.TextInput(attrs={'class': 'form-control'}),
            # 'priority':forms.NumberInput(attrs={'class': 'form-control'}),
            # 'lng':forms.TextInput(attrs={'class': 'form-control'}),
            # 'lat':forms.TextInput(attrs={'class': 'form-control'})
        }


    def __init__(self, *args, **kwargs):
        cur_site = kwargs.pop('site')
        super(CityForm, self).__init__(*args, **kwargs)
        self.fields['region'].queryset = City.objects.filter(site=cur_site).filter(is_region=True)


class NgCityForm(NgModelFormMixin, NgFormValidationMixin, CityForm, Bootstrap3FormMixin):
    form_name = 'submit_data_form'
    scope_prefix = 'submit_data'