from djangular.forms import NgFormValidationMixin, NgModelFormMixin, NgModelForm
from djangular.styling.bootstrap3.forms import Bootstrap3Form, Bootstrap3FormMixin
from django import forms

class SendBitcoinsForm(Bootstrap3Form):
    to = forms.CharField(label='To', min_length=10, max_length=50, required=True, widget=forms.TextInput(attrs={'placeholder': 'enter a valid btc address'}))
    amount = forms.FloatField(min_value=0.00000001, label='Amount', required=True)
    message = forms.CharField(label='Message', required=False,
        widget=forms.Textarea(attrs={'rows': '3'}))

class NgSendBitcoinsForm(NgModelFormMixin, NgFormValidationMixin, SendBitcoinsForm):
    form_name = "send_btc_form"
    scope_prefix = 'submit_data'
