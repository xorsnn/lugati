# -*- coding: utf-8 -*-
from django import forms
from lugati.lugati_shop.models import PhoneNumber
from lugati.products.models import Brand
from django.forms import Textarea, HiddenInput
from registration.forms import RegistrationForm
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, SetPasswordForm, AdminPasswordChangeForm
from djangular.forms import NgFormValidationMixin, NgModelFormMixin
from djangular.styling.bootstrap3.forms import Bootstrap3Form, Bootstrap3FormMixin
from registration.users import UserModel
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        widgets = {
            'site': HiddenInput(),
        }

def validate_email(value):
    existing = UserModel().objects.filter(email__iexact=value)
    if not existing.exists():
        raise forms.ValidationError(_("A user with that email doesn't exists."))

class LugatiPasswordRestoreRequestForm(NgFormValidationMixin, NgModelFormMixin, Bootstrap3Form):
    email = forms.EmailField(label='E-Mail', required=True, help_text='Please enter your email address', validators=[validate_email])
    scope_prefix = 'password_restore_request_data'
    form_name = 'password_restore_request_form'


class LugatiPasswordRestoreForm(NgFormValidationMixin, NgModelFormMixin, Bootstrap3Form):
    request_code = forms.CharField(max_length=100, widget=forms.HiddenInput(), required=True)

    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    new_password1 = forms.CharField(label=_("New password"),
                                    widget=forms.PasswordInput)
    new_password2 = forms.CharField(label=_("New password confirmation"),
                                    widget=forms.PasswordInput)

    scope_prefix = 'password_restore_data'
    form_name = 'password_restore_form'


    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        return password2

class LugatiAuthForm(NgFormValidationMixin, NgModelFormMixin, AuthenticationForm, Bootstrap3Form):
    scope_prefix = 'auth_data'
    form_name = 'auth_form'

class LugatiRegistrationForm(NgFormValidationMixin, NgModelFormMixin, RegistrationForm, Bootstrap3Form):
    def clean_email(self):
        """
        Validate that the username is alphanumeric and is not already
        in use.

        """
        existing = UserModel().objects.filter(email__iexact=self.cleaned_data['email'])
        if existing.exists():
            raise forms.ValidationError(_("A user with that email already exists."))
        else:
            return self.cleaned_data['email']
    scope_prefix = 'register_data'
    form_name = 'register_form'