# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from lugati.lugati_mobile.models import LugatiDevice
from lugati.lugati_shop.models import Shop
import json

def api_devices(request):
    res_dt = {
        'operation': 'none'
    }
    
    dev_state = {}
    dev_id = request.GET['dev_id']
    reg_id = request.GET['reg_id']

    dev_name = ''
    if 'dev_name' in request.GET:
        dev_name = request.GET['dev_name']
    shop_id = ''
    if 'shop_id' in request.GET:
        shop_id = request.GET['shop_id']

    #shop_name = request
    try:
        device = LugatiDevice.objects.get(dev_id=dev_id)
        if dev_name <> '':
            device.name = dev_name
        if shop_id <> '':
            device.shop = Shop.objects.get(pk=shop_id)
        device.save()

        dev_state['dev_name'] = ''
        if device.name:
            dev_state['dev_name'] = device.name
        dev_state['shop_id'] = ''
        if device.shop:
            dev_state['shop_id'] = device.shop.id
        res_dt['dev_state'] = dev_state
        res_dt['operation'] = 'already_registered'
    except:
        device = LugatiDevice()
        device.dev_id = dev_id
        device.reg_id = reg_id
        if dev_name <> '':
            device.name = dev_name
        if shop_id <> '':
            device.shop = Shop.objects.get(pk=shop_id)
        device.save()

        dev_state['dev_name'] = ''
        if device.name:
            dev_state['dev_name'] = device.name
        dev_state['shop_id'] = ''
        if device.shop:
            dev_state['shop_id'] = device.shop.id

        res_dt['dev_state'] = dev_state
        res_dt['operation'] = 'registered'

    return HttpResponse(json.dumps(res_dt))