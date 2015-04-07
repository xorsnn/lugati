# -*- coding: utf-8 -*-

from djangular.forms import NgFormValidationMixin, NgModelFormMixin
from django import forms
from .models import LugatiNewsletterSignUp
from djangular.styling.bootstrap3.forms import Bootstrap3Form
class LugatiFeedbackForm(NgModelFormMixin, NgFormValidationMixin, Bootstrap3Form):
    name = forms.CharField(max_length=100, label=u"Ваше имя:")
    subject = forms.CharField(max_length=50, label=u"Тема:")
    mail = forms.EmailField(label=u"email:")
    phone = forms.CharField(max_length=20, required=False, label=u"Телефон для связи:")
    message = forms.CharField(required=False, label=u"Текст сообщения:")

    form_name = "confirm_order_form"
    scope_prefix = 'submit_data'

class LugatiNewsletterSignUpForm(forms.ModelForm):
    class Meta:
        model = LugatiNewsletterSignUp
        widgets = {
            'site': forms.HiddenInput(),
            'email': forms.EmailInput(attrs={'class': 'form-control'})
        }

class NgLugatiNewsletterSignUpForm(NgModelFormMixin, NgFormValidationMixin, LugatiNewsletterSignUpForm):
    form_name = "confirm_order_form"
    scope_prefix = "submit_data"