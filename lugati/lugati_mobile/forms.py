# -*- coding: utf-8 -*-


from djangular.forms import NgFormValidationMixin, NgModelFormMixin
from django import forms
from lugati.lugati_shop.models import ShoppingPlace
from lugati.lugati_mobile.models import LugatiDevice
from django.forms import Textarea, HiddenInput


# class LugatiClerkForm(forms.ModelForm):
#
#     #def __init__(self, *args, **kwargs):
#     #    cur_site = kwargs.pop('site')
#     #    super(LugatiClerkForm, self).__init__(*args, **kwargs)
#     #
#     #
#     #    self.fields['shopping_place'] = forms.ModelChoiceField(queryset=ShoppingPlace.objects.filter(site=cur_site),
#     #                                                         widget=forms.Select(attrs={'class':'form-control'}),
#     #                                                         required=False,
#     #                                                         label=_(u'Shopping place'))
#
#
#
#     class Meta:
#         model = LugatiDevice
#         widgets = {
#             'shop': HiddenInput(),
#             'dev_id': forms.TextInput(attrs={'class': 'form-control'}),
#             'reg_id': forms.TextInput(attrs={'class': 'form-control'}),
#             'name': forms.TextInput(attrs={'class': 'form-control'}),
#             'is_active': forms.CheckboxInput(attrs={'class': 'form-control'}),
#         }
#
# class NgLugatiDeviceForm(NgFormValidationMixin, NgModelFormMixin, LugatiClerkForm):
#     form_name = "submit_data_form"
#     scope_prefix = 'submit_data'