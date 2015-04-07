from django.db import models
from lugati.lugati_shop.models import LugatiCompany
from django.db.models import Count, Min, Sum, Avg
import logging
logger = logging.getLogger(__name__)
import stomp
import json
# from lugati.lugati_payment.payment_procs import get_pending_btc_proc
from decimal import Decimal
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone

stomp_conn = stomp.Connection()
stomp_conn.start()
stomp_conn.connect()

class LugatiExchangeRate(models.Model):
    symbol = models.CharField(max_length=50, primary_key=True)
    rate = models.DecimalField(decimal_places=8, max_digits=15)

    def get_list_item_info(self, request=None):
        node = {
            'id': self.symbol,
            'symbol': self.symbol,
            'rate': "%.8f" % self.rate
        }
        return node


class PaymentTransaction(models.Model):
    sum = models.DecimalField(decimal_places=8, max_digits=10)
    custom = models.CharField(max_length=200)

class PaymentOption(models.Model):
    company = models.ForeignKey(LugatiCompany)
    name = models.CharField(max_length=200)

class BTCPaymentTransaction(models.Model):
    company = models.ForeignKey(LugatiCompany)
    sum = models.DecimalField(decimal_places=8, max_digits=15)
    msg = models.TextField(default='')
    from_address = models.CharField(max_length=100)
    to_address = models.CharField(max_length=100)

    dt_add = models.DateTimeField(auto_now_add=True, editable=False)

    def save(self, *args, **kwargs):
        super(BTCPaymentTransaction, self).save(*args, **kwargs)
        try:
            balance = BTCPaymentTransaction.objects.filter(company=self.company).aggregate(Sum('sum'))
            bal_sum = balance['sum__sum']
            if not bal_sum:
                bal_sum = Decimal(0)

            #pending btc
            delta = timedelta(seconds=settings.TRANSACTONS_PENDING_TIME_SECONDS)
            pending_balance = BTCPaymentTransaction.objects.filter(company=self.company).filter(sum__gt=0).filter(dt_add__gt=timezone.now()-delta).aggregate(Sum('sum'))
            pending_bal_sum = pending_balance['sum__sum']
            if not pending_bal_sum:
                pending_bal_sum = Decimal(0)

            stomp_conn.send(body=json.dumps({'message': 'btc_balance_changed', 'btc_balance': str(bal_sum), 'btc_pending': str(pending_bal_sum)}),
                destination='/topic/' + 'payment_channel_btc_balance_' + str(self.company.id))
        except Exception, e:
            logger.info('err:' + str(e))