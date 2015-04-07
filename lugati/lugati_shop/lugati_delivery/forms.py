# -*- coding: utf-8 -*-
from django import forms
from .models import DeliveryOption, DeliveryPrice
from django.forms import Textarea, HiddenInput
from django.utils.translation import ugettext as _
from lugati.lugati_points_of_sale.models import City
from djangular.forms import NgFormValidationMixin, NgModelFormMixin, NgModelForm
from lugati.products.models import Product
from django.contrib.sites.models import get_current_site
from djangular.styling.bootstrap3.forms import Bootstrap3Form, Bootstrap3FormMixin


class DeliveryOptionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')

        super(DeliveryOptionForm, self).__init__(*args, **kwargs)

        cur_site = get_current_site(request)

        self.fields['city'] = forms.ModelChoiceField(queryset=City.objects.filter(site=cur_site),
                                                     widget=forms.Select(attrs={'class': 'form-control'}),
                                                     label=_(u'Город'),
                                                     required=False)

        # self.fields['products'] = forms.ModelMultipleChoiceField(queryset=Product.objects.filter(site=cur_site).filter(is_category=False),
        # widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        #                                              label=_(u'Products'),
        #                                              required=False)

    class Meta:
        model = DeliveryOption
        widgets = {
            # 'site': HiddenInput(),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            # 'price': forms.NumberInput(attrs={'class':'form-control'}),
            'price': forms.HiddenInput(),
            # 'additional_price': forms.NumberInput(attrs={'class':'form-control'}),
            'additional_price': forms.HiddenInput(),
            'online_payment': forms.CheckboxInput(attrs={'class': 'form-control'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-control'}),
            'site': forms.HiddenInput(),
            'del_opt': forms.NumberInput(attrs={'class': 'form-control'}),
            'mail_text': forms.Textarea(attrs={'class': 'form-control'}),
            'products': forms.HiddenInput(),
        }


class NgDeliveryOptionForm(NgFormValidationMixin, NgModelFormMixin, DeliveryOptionForm):
    form_name = "submit_data_form"
    scope_prefix = 'submit_data'


class DeliveryPriceForm(NgModelForm):
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super(DeliveryPriceForm, self).__init__(*args, **kwargs)

        cur_site = get_current_site(request)

        # self.fields['product'] = forms.ModelChoiceField(queryset=Product.objects.filter(site=cur_site).filter(is_category=False),
        # widget=forms.Select(attrs={'class': 'form-control'}),
        #                                              label=_(u'Product'),
        #                                              required=True)
        #
        # self.fields['delivery_option'] = forms.ModelChoiceField(queryset=DeliveryOption.objects.filter(site=cur_site),
        #                                              widget=forms.Select(attrs={'class': 'form-control'}),
        #                                              label=_(u'Delivery option'),
        #                                              required=True)
        self.fields['product'].queryset = Product.objects.filter(site=cur_site).filter(is_category=False)

        self.fields['delivery_option'].queryset = DeliveryOption.objects.filter(site=cur_site)


    class Meta:
        model = DeliveryPrice


class NgDeliveryPriceForm(NgFormValidationMixin, NgModelFormMixin, DeliveryPriceForm, Bootstrap3FormMixin):
    form_name = "submit_data_form"
    scope_prefix = 'submit_data'
