# -*- coding: utf-8 -*-
from robokassa.forms import RobokassaForm
from django.shortcuts import render
from django.http import HttpResponse
import json
from django.conf import settings
from django.contrib.sites.models import get_current_site
from lugati.lugati_shop.lugati_orders.models import Order
import logging
from django.template.loader import get_template
from django.template import Context, Template
from lugati.lugati_shop.lugati_orders.models import OrderItem
from django.core.mail import EmailMultiAlternatives
from lugati.lugati_shop.models import PhoneNumber
from twilio.rest import TwilioRestClient
import decimal

client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

logger = logging.getLogger(__name__)

def result(request):
    hasTickets = False
    cur_site = get_current_site(request)
    logger.info('robokassa result' + str(request.GET))
    order = Order.objects.get(pk=request.GET['InvId'])

    send_mail = order.paid
    try:
        #inv_id=107&InvId=107&out_summ=1.000000&OutSum=1.000000&crc=ace54a1807a6204b088a354cae50d40d&SignatureValue=ace54a1807a6204b088a354cae50d40d&Culture=ru
        logger.info('robokassa updating order')
        order.paid = True
        order.save()
        logger.info('robokassa order ' + str(order.id) + ' paid')
    except Exception, e:
        logger.info('robokassa error: ' + str(e))

    try:
        for item in OrderItem.objects.filter(order=order):
            if item.product.parent_object:
                if item.product.parent_object.name.lower() == u'билеты':
                    hasTickets = True
            break
    except Exception, e:
        logger.info('has tick error: ' + str(e))

    if send_mail <> order.paid:
        try:
            cur_context = { 'order_id': order.id,
                             'paid': True,
                             'cart_items': OrderItem.objects.filter(order=order),
                             'mail': True,
                             'email': order.email,
                             'phone': order.phone,
                             'address': order.address,
                             'city': order.city,
                             'zip_code': order.zip_code,
                             'name': order.name,
                             'shop_name': cur_site.name,
                             'delivery_price': order.delivery_price,
                             'total': (decimal.Decimal(order.get_total_sum()) + decimal.Decimal(order.delivery_price)),
                             'payment_method': u'ОПЛАТА ONLINE',
                             'del_var': 1}

            header_text = ''
            del_option = order.delivery_option
            if del_option:
                try:
                    header_t = Template(del_option.mail_text.replace('{$', '{{').replace('$}', '}}'))
                    header_text = header_t.render(Context(cur_context))
                except Exception, e:
                    logger.info('submit_err: ' + str(e))
            logger.info('header text: ' + header_text)
            cur_context['header_text'] = header_text

            t = get_template('custom/' + cur_site.name + '/catalog/mail_template.html')
            message_html = t.render(Context(cur_context))
            #
            # message_html = t.render(Context({'order_id': order.id,
            #                                  'paid': True,
            #                                  'cart_items': OrderItem.objects.filter(order=order),
            #                                  'mail': True,
            #                                  'email': order.email,
            #                                  'phone': order.phone,
            #                                  'address': order.address,

            #                                  'name': order.name,
            #                                  'shop_name': cur_site.name,
            #                                  'delivery_price': order.delivery_price,
            #                                  'total': decimal.Decimal(order.get_total_sum()) + decimal.Decimal(order.delivery_price)}))

        except:
            logger.info('robokassa exeption')
            t = get_template('lugati_shop/order_mail.html')
            message_html = t.render(Context({'order_id': order.id,
                                             'paid': True,
                                             'cart_items': OrderItem.objects.filter(order=order),
                                             'mail': True,
                                             'email': order.email,
                                             'phone': order.phone,
                                             'address': order.address,
                                             'name': order.name,
                                             'shop_name': cur_site.name,
                                             'delivery_price': order.delivery_price,
                                             'total': decimal.Decimal(order.get_total_sum()) + decimal.Decimal(order.delivery_price)}))

        subject = str(cur_site.domain) + ': Ваш заказ № ' + str(order.id)
        emails  = [order.email]
        try:
            msg = EmailMultiAlternatives(subject, message_html, settings.DEFAULT_FROM_EMAIL, emails)
            #msg = EmailMultiAlternatives(subject, message_text, settings.DEFAULT_FROM_EMAIL, emails)
            msg.attach_alternative(message_html, "text/html")
            msg.send()
        except Exception, e:
            logger.error(str(e))
        #to us
        if (hasTickets):
            emails = [settings.DEFAULT_TICKETS_EMAIL]
        else:
            emails  = [settings.DEFAULT_FROM_EMAIL]

        try:
            msg = EmailMultiAlternatives(subject, message_html, settings.DEFAULT_FROM_EMAIL, emails)
            msg.attach_alternative(message_html, "text/html")
            msg.send()
        except Exception, e:
            logger.error(str(e))

        for phone_number in PhoneNumber.objects.filter(site=cur_site):
            try:
                message = client.sms.messages.create(body=(unicode(u'новый заказ в магазине ') + cur_site.name),
                            to=(phone_number.number), # Replace with your phone number
                            from_=settings.TWILIO_PHONE_NUMBER) # Replace with your Twilio number

            except Exception, e:
                logger.error(str(e))


    return HttpResponse()

def success(request):
    cur_site_name = get_current_site(request).name
    cur_site = get_current_site(request)
    logger.info('robokassa success' + str(request.GET))
    order = Order.objects.get(pk=request.GET['InvId'])

    return render(request, 'ligati_payment/lugati_robokassa/success.html', {'cur_site_name': cur_site_name})

def fail(request):
    cur_site_name = get_current_site(request).name
    logger.info('robokassa fail' + str(request.GET))
    return HttpResponse()

def get_payment_template(request, order_id=''):
    if order_id == '':
        return HttpResponse()
    else:
        cur_site_name = get_current_site(request).name
        order = Order.objects.get(pk=order_id)
        if settings.LUGATI_TESTING:
            form = RobokassaForm(initial={
                'OutSum': 1,
                'InvId': order_id,
            })
        else:
            form = RobokassaForm(initial={
                'OutSum': float(order.delivery_price) + float(order.get_total_sum()),
                'InvId': order_id,
            })

        return render(request, 'ligati_payment/lugati_robokassa/robokassa_payment_template.html', {'form': form,
                                                                                                   'cur_site_name': cur_site_name})
