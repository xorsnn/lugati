# -*- coding: utf-8 -*-
from django import template
register = template.Library()
from django.template import Library, Node, TemplateSyntaxError
from lugati.lugati_payment.forms import NgSendBitcoinsForm

@register.inclusion_tag('lugati_admin/lugati_version_1_0/include/send_btc_form_block.html', takes_context=True)
def send_btc_form_tag(context):
    request = context['request']
    return {
        'form': NgSendBitcoinsForm
    }

