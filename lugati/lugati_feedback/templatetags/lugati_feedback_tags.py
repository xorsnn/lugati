# -*- coding: utf-8 -*-
from django import template
from django.core.urlresolvers import resolve
from django.template import Library, Node, TemplateSyntaxError
from django.contrib.contenttypes.models import ContentType
from lugati.lugati_feedback.forms import LugatiFeedbackForm
from django.contrib.sites.models import get_current_site
from lugati.lugati_feedback.forms import NgLugatiNewsletterSignUpForm
register = Library()

@register.inclusion_tag('lugati_feedback/lugati_feedback.html', takes_context=True)
def lugati_feedback_form(context):
    request = context['request']
    return {
        'form': LugatiFeedbackForm
    }

@register.inclusion_tag('lugati_feedback/lugati_newsletter_singup.html', takes_context=True)
def lugati_newsletter_singup_form(context):
    request = context['request']
    cur_site = get_current_site(request)

    return {
        'form': NgLugatiNewsletterSignUpForm(initial={'site':cur_site})
    }
