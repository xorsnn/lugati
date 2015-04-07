# -*- coding: utf-8 -*-

from registration.forms import RegistrationForm, RegistrationFormUniqueEmail

from djangular.forms import NgFormValidationMixin, NgModelFormMixin
from django import forms
from django.utils.translation import ugettext_lazy as _

class LugatiRegistrationForm(RegistrationFormUniqueEmail):
    form_name = "confirm_order_form"
    scope_prefix = 'submit_data'

