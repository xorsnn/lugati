# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse
import json
from django.contrib.sites.models import get_current_site
from lugati.lugati_feedback.forms import LugatiFeedbackForm
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from lugati.lugati_feedback.forms import NgLugatiNewsletterSignUpForm
from lugati.lugati_feedback.models import LugatiNewsletterSignUp
from lugati.lugati_feedback.models import MpsFeedback
import json

import logging
logger = logging.getLogger(__name__)

def mps_feedback(request):
    res_dt = {}
    res_dt['error'] = False
    try:
        feedback = MpsFeedback()
        feedback.name = request.GET['email']
        feedback.text = request.GET['message']
        feedback.save()
    except:
        res_dt['error'] = True

    return HttpResponse(json.dumps(res_dt))

def lugati_newsletter_sing_up(request):
    cur_site = get_current_site(request)
    try:
        form = NgLugatiNewsletterSignUpForm(data=request.GET)
        if not LugatiNewsletterSignUp.objects.filter(site=cur_site).filter(email=request.GET['email']).exists():
            form.save()
    except:
        pass
    return HttpResponse(json.dumps({}))

def lugati_feedback(request):
    cur_site = get_current_site(request)
    form = LugatiFeedbackForm(request.POST)
    if form.is_valid():
        message = form.cleaned_data['message']
        name = form.cleaned_data['name']
        subject = form.cleaned_data['subject']
        mail = form.cleaned_data['mail']
        phone = form.cleaned_data['phone']

        message_text = ""
        message_text += u"от: " + unicode(name) + " (" + unicode(mail) + ")\n"
        message_text += u"тема: " + unicode(subject) + "\n"
        message_text += u"телефон для связи: " + unicode(phone) + "\n"
        message_text += u"текст: " + unicode(message)

        #to us
        emails  = [settings.DEFAULT_FROM_EMAIL]
        try:
            msg = EmailMultiAlternatives(u"вопрос с сайта primorsk.su", message_text, settings.DEFAULT_FROM_EMAIL, emails)
            msg.send()
        except Exception, e:
            logger.error(str(e))

        return HttpResponse(json.dumps({'response': "Email with a confirmation link has been sent", 'result': 'success'}))
    else:
        return HttpResponse(json.dumps({'response': "Form invalid", 'result': 'error'}))