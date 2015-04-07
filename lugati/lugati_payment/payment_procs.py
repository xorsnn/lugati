from lugati.lugati_payment.models import BTCPaymentTransaction
from decimal import *
from django.db.models import Count, Min, Sum, Avg
import requests
from lugati.lugati_payment.models import LugatiExchangeRate
from django.conf import settings
from datetime import datetime, timedelta
from django.utils import timezone

def update_curreynce_exchange_rates():
    res = requests.get('https://api.coinbase.com/v1/currencies/exchange_rates')
    res_dt = res.json()
    for key in res_dt:
        try:
            rate = LugatiExchangeRate.get(pk=key)
        except:
            rate = LugatiExchangeRate()
            rate.symbol = key
        rate.rate = Decimal(res_dt[key])
        rate.save()

def get_currency_exchange_rate_proc(currency_from, currency_to):
    from_str = str(currency_from).lower()
    to_str = str(currency_to).lower()
    rate = None
    try:
        rate = LugatiExchangeRate.objects.get(pk=(from_str + '_to_' + to_str))
    except Exception, e:
        pass
    return rate

def get_btc_balance_proc(cur_company):
    balance = BTCPaymentTransaction.objects.filter(company=cur_company).aggregate(Sum('sum'))
    bal_sum = balance['sum__sum']
    if not bal_sum:
        bal_sum = 0
    return bal_sum

def get_pending_btc_proc(cur_company):
    # now = datetime.now
    delta = timedelta(seconds=settings.TRANSACTONS_PENDING_TIME_SECONDS)
    balance = BTCPaymentTransaction.objects.filter(company=cur_company).filter(sum__gt=0).filter(dt_add__gt=timezone.now()-delta).aggregate(Sum('sum'))
    bal_sum = balance['sum__sum']
    if not bal_sum:
        bal_sum = 0
    return bal_sum