# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from lugati.lugati_widgets.models import LugatiNews
from django.db.models.signals import post_save
from lugati.lugati_shop.lugati_orders.models import Order

class MpsFeedback(models.Model):
    name = models.CharField(max_length=100)
    text = models.TextField()
    order = models.ForeignKey(Order, null=True, blank=True)

class LugatiFeedbackForm(models.Model):
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    mail = models.EmailField()
    message = models.TextField()

class LugatiNewsletterSignUp(models.Model):
    email = models.EmailField()
    site = models.ForeignKey(Site)

class LugatiNewsletterTask(models.Model):
    done = models.BooleanField(default=False)
    content_type    = models.ForeignKey(ContentType, null=True, blank=True)
    object_id       = models.PositiveIntegerField(null=True, blank=True)
    content_object  = generic.GenericForeignKey('content_type', 'object_id')

def create_newsletter_task(sender, **kw):
    new_task = LugatiNewsletterTask()
    new_task.content_object = kw['instance']
    new_task.save()

post_save.connect(create_newsletter_task, sender=LugatiNews, dispatch_uid="news-creation-signal")