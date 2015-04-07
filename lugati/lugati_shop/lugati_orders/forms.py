# -*- coding: utf-8 -*-

from djangular.forms import NgFormValidationMixin, NgModelFormMixin
from django import forms
from lugati.lugati_shop.models import ShoppingPlace
from django.forms import Textarea, HiddenInput
from lugati.lugati_shop.lugati_orders.models import Order

from djangular.forms import NgFormValidationMixin, NgModelFormMixin

class LugatiOrderEditForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(LugatiOrderEditForm, self).__init__(*args, **kwargs)

        self.fields['delivery_price'] = forms.DecimalField(widget=forms.NumberInput(attrs={'class':'form-control'}), required=False)

    class Meta:
        model = Order


        widgets = {
            'order_num': HiddenInput(),
            # 'paid': HiddenInput(),
            'paid': forms.TextInput(attrs={'readonly': 'readonly','class':'form-control'}),
            'delivered': HiddenInput(),
            # 'delivery_price': HiddenInput(),
            'delivery_price': forms.NumberInput(attrs={'readonly': 'readonly','class':'form-control'}),
            'cart_id': HiddenInput(),
                #'cart_id': forms.TextInput(attrs={'readonly': 'readonly'}),
            'site': HiddenInput(),
            'shopping_place': HiddenInput(),
            'state': forms.RadioSelect(attrs={'class':'btn btn-primary'}),
            # 'delivery_price': forms.NumberInput(attrs={'class':'form-control'}),
            'address': forms.Textarea(attrs={'class':'form-control'}),
            'email': forms.TextInput(attrs={'class':'form-control'}),
            'phone': forms.TextInput(attrs={'class':'form-control'}),
            'city': forms.TextInput(attrs={'class':'form-control'}),
            'zip_code': forms.TextInput(attrs={'class':'form-control'}),
            'name': forms.TextInput(attrs={'class':'form-control'}),
            'tracking number': forms.TextInput(attrs={'class':'form-control'}),
            'receipt_path': forms.HiddenInput()
        }

class NgLugatiOrderEditForm(NgModelFormMixin, NgFormValidationMixin, LugatiOrderEditForm):
    form_name = 'submit_data_form'
    scope_prefix = 'submit_data'