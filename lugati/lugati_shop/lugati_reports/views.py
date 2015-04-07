from django.shortcuts import render
from django.http import HttpResponse
from lugati.lugati_registration.models import LugatiUserProfile
from lugati.lugati_shop.lugati_orders.models import Order
from lugati.lugati_shop.models import ShoppingPlace, Shop
import json
import datetime


def compose_table_by_days(profile, orders):
    res = {}

    week_delta = datetime.timedelta(days=7)
    day_delta = datetime.timedelta(days=1)
    old_day = None

    places = ShoppingPlace.objects.filter(shop__in=Shop.objects.filter(company=profile.get_company()))
    for place in places:
        res[str(place.id)] = {
            'name': place.name,
            'values': []
        }

    for order in orders:
        cur_day = datetime.datetime(order.dt_add.year, order.dt_add.month, order.dt_add.day)

        if old_day <> cur_day:
            for key in res:
                if key == str(order.id):
                    res[key]['values'].append(order.get_total_sum())
                else:
                    res[key]['values'].append(0)

            old_day = cur_day
        else:
            res[str(order.shopping_place.id)]['values'][len(res[str(order.shopping_place.id)]['values'])-1] += order.get_total_sum()
    return res


def get_weekly_report(request):
    res_dt = {
        'total': 0,
        'tables': {},
        'dates': []
    }
    prof = LugatiUserProfile.objects.get(user=request.user)

    orders = Order.objects.filter(shopping_place__in=ShoppingPlace.objects.filter(shop__in=Shop.objects.filter(company=prof.get_company()))).order_by('-dt_add')

    for order in orders:

        if order.shopping_place.name in res_dt['tables']:
            res_dt['tables'][order.shopping_place.name]['total'] += order.get_total_sum()
        else:
            res_dt['tables'][order.shopping_place.name] = {
                'total': order.get_total_sum(),
                'by_day': []
            }



        res_dt['total'] += order.get_total_sum()

    table_by_days = compose_table_by_days(prof, orders)
    res_dt['by_days'] = table_by_days

    return HttpResponse(json.dumps(res_dt))