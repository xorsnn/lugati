# -*- coding: utf-8 -*-
from django.utils.translation import ugettext as _
from djangular.forms import NgFormValidationMixin, NgModelFormMixin, NgModelForm
from django import forms
from lugati.lugati_shop.models import ShoppingPlace
from .models import PhoneNumber
from django.forms import Textarea, HiddenInput
from lugati.lugati_shop.models import Shop
from django.forms import ModelForm
from lugati.lugati_mobile.models import LugatiDevice
from lugati.lugati_shop.models import LugatiCompany, LugatiClerk
from lugati.lugati_registration.models import LugatiUserProfile
from django.contrib.auth.models import User
from djangular.styling.bootstrap3.forms import Bootstrap3Form, Bootstrap3FormMixin

class CofirmOrderForm(forms.Form):
    name = forms.CharField(max_length=100, label=u"Ваше имя:")
    phone = forms.CharField(max_length=50, label=u"Телефон:")
    mail = forms.EmailField(label=u"email:")
    address = forms.CharField(widget=forms.Textarea,required=False, label=u"Ваш адрес:")
    city = forms.CharField(max_length=200, label=u"Город:")
    zip_code = forms.CharField(max_length=200, label=u"Индекс:")
    sola_delivery_option = forms.CharField(max_length=200, label=u"ИД доставки:")

class LugatiCofirmOrderForm(NgModelFormMixin, NgFormValidationMixin, forms.Form):
    name = forms.CharField(max_length=100, label=u"Ваше имя:", widget=forms.TextInput(attrs={'class':'form-control'}))
    phone= forms.CharField(max_length=50, label=u"Телефон:", widget=forms.TextInput(attrs={'class':'form-control'}))
    mail = forms.EmailField(label=u"email:", widget=forms.EmailInput(attrs={'class':'form-control'}))
    address=forms.CharField(widget=forms.Textarea(attrs={'class':'form-control'}), required=False, label=u"Ваш адрес:")

    form_name = "confirm_order_form"
    scope_prefix = 'submit_data'


class LugatiShoppingPlaceForm(NgModelForm):

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super(LugatiShoppingPlaceForm, self).__init__(*args, **kwargs)

        self.fields['shop'] = forms.ModelChoiceField(queryset=Shop.objects.filter(company=LugatiUserProfile.objects.get(user=request.user).get_company()),
                                                        initial=Shop.objects.filter(company=LugatiUserProfile.objects.get(user=request.user).get_company())[0],
                                                        widget=forms.HiddenInput())
    class Meta:
        model = ShoppingPlace
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'bottom_title': forms.HiddenInput(),
            'top_title': forms.HiddenInput()
        }

class NgShoppingPlaceForm(NgFormValidationMixin, NgModelFormMixin, LugatiShoppingPlaceForm, Bootstrap3FormMixin):
    form_name = "submit_data_form"
    scope_prefix = 'submit_data'

class NgEditShoppingPlaceForm(NgFormValidationMixin, NgModelFormMixin, LugatiShoppingPlaceForm):
    form_name = "submit_data_form"
    scope_prefix = 'submit_data'
    class Meta:
        model = ShoppingPlace
        widgets = {
            'name': forms.HiddenInput(),
            'bottom_title': forms.HiddenInput(),
            'top_title': forms.HiddenInput()
        }

class PhoneForm(forms.ModelForm):
    class Meta:
        model = PhoneNumber
        widgets = {
            'site': HiddenInput(),
        }

class ShopForm(ModelForm):
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super(ShopForm, self).__init__(*args, **kwargs)

        self.fields['company'] = forms.ModelChoiceField(queryset=LugatiCompany.objects.filter(pk=LugatiUserProfile.objects.get(user=request.user).get_company().id),
                                                             widget=forms.Select(attrs={'class':'form-control'}),
                                                             required=True,
                                                             initial=LugatiUserProfile.objects.get(user=request.user).get_company(),
                                                             label=_(u'Company'))
    class Meta:
        model = Shop
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'background_color': HiddenInput(),
            'text_color': HiddenInput(),
            'text_font': HiddenInput(),
            'font_size': HiddenInput()
        }

class NgShopForm(NgFormValidationMixin, NgModelFormMixin, ShopForm):
    form_name = "submit_data_form"
    scope_prefix = 'submit_data'


# class LugatiCompanyForm(ModelForm):
class LugatiCompanyForm(NgModelForm):

    class Meta:
        model = LugatiCompany
        exclude = ['company_logo']
        widgets = {
            # 'name': forms.TextInput(attrs={'class': 'form-control'}),
            # 'default_currency': forms.Select(attrs={'class':'form-control'}),
            'top_title': HiddenInput(),
            'bottom_title': HiddenInput(),
        }

class NgLugatiCompanyForm(NgFormValidationMixin, NgModelFormMixin,  LugatiCompanyForm, Bootstrap3FormMixin):
    form_name = "submit_data_form"
    scope_prefix = 'submit_data'


class LugatiClerkForm(NgModelForm):

    pic_array = forms.CharField(required=False, widget=HiddenInput)

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super(LugatiClerkForm, self).__init__(*args, **kwargs)

        self.fields['company'] = forms.ModelChoiceField(queryset=LugatiCompany.objects.filter(pk=LugatiUserProfile.objects.get(user=request.user).get_company().id),
                                                        initial=LugatiUserProfile.objects.get(user=request.user).get_company(),
                                                        widget=forms.HiddenInput())

        self.fields['branch'] = forms.ModelChoiceField(queryset=Shop.objects.filter(company=LugatiUserProfile.objects.get(user=request.user).get_company()),
                                                        initial=Shop.objects.filter(company=LugatiUserProfile.objects.get(user=request.user).get_company())[0],
                                                        widget=forms.HiddenInput())

    class Meta:
        model = LugatiClerk
        exclude = ['user', 'login']
        widgets = {
            'reg_id': forms.HiddenInput(),
            'device': forms.HiddenInput(),
            'user': forms.HiddenInput(),
        }

class NgLugatiClerkForm(NgFormValidationMixin, NgModelFormMixin, LugatiClerkForm, Bootstrap3FormMixin):
    form_name = "submit_data_form"
    scope_prefix = 'submit_data'