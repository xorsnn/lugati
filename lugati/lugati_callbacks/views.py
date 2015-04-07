from django.shortcuts import render
from django.http import HttpResponse
from pyxmpp2.simple import send_message
import logging
from django.views.decorators.csrf import csrf_exempt
logger = logging.getLogger(__name__)

@csrf_exempt
def test_callback(request):

    logger.info('callback ' + str(request.POST))

    your_jid = 'xors.nn@gmail.com'
    your_password = 'OhN3Ag3Uid'
    target_jid = 'suslov.kirill@gmail.com'
    message = 'test message'

    send_message(your_jid, your_password, target_jid, message)

    return HttpResponse()