#!/usr/bin/python
# example based on http://thomas.pelletier.im/2010/08/websocket-tornado-redis/

hmac_key = 'secret'

import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import hmac
import re
import time
import sys
import optparse
import json
from lugati.lugati_exchange.models import Instrument
from django.conf import settings
import urllib
from django.core.management.base import BaseCommand, CommandError
import sys
from PyQt4 import QtCore, QtGui, QtWebKit
from django.core.files.uploadedfile import InMemoryUploadedFile
import cStringIO
import StringIO
from PIL import Image
from lugati.lugati_media.models import ThebloqImage

import logging
logger = logging.getLogger(__name__)

app = QtGui.QApplication([])

class Capturer(QtCore.QObject):
    ready_trigger = QtCore.pyqtSignal()
    loop = QtCore.QEventLoop()
    def __init__(self):
        super(Capturer, self).__init__()
        self.saw_initial_layout = False
        self.saw_document_complete = False



    def loadFinishedSlot(self):
        print 'load finished'
        self.saw_document_complete = True
        if self.saw_initial_layout and self.saw_document_complete:
            self.ready_trigger.emit()

    def initialLayoutSlot(self):
        print 'initial layout'
        self.saw_initial_layout = True
        if self.saw_initial_layout and self.saw_document_complete:
            self.ready_trigger.emit()

    def contentsSizeChangedSlot(self, size):
        print 'size changed'

    def capture(self, html_str):

        logger.info('1')
        self.wb = QtWebKit.QWebPage()
        self.wb.loadFinished.connect(self.loadFinishedSlot)
        self.wb.mainFrame().initialLayoutCompleted.connect(self.initialLayoutSlot)
        self.wb.mainFrame().setScrollBarPolicy(
            QtCore.Qt.Horizontal, QtCore.Qt.ScrollBarAlwaysOff)
        self.wb.mainFrame().setScrollBarPolicy(
            QtCore.Qt.Vertical, QtCore.Qt.ScrollBarAlwaysOff)
        logger.info('2')
        self.wb.mainFrame().setHtml(html_str)
        logger.info('3')
        # self.ready_trigger.connect(self.loop.exit)
        # self.loop.exec_()
        while not (self.saw_initial_layout and self.saw_document_complete):
            self.loop.processEvents()
            logger.info('4')
        self.saw_initial_layout = False
        self.saw_document_complete = False
        logger.info('5')
        self.wb.setViewportSize(self.wb.mainFrame().contentsSize())
        img = QtGui.QImage(self.wb.viewportSize(), QtGui.QImage.Format_ARGB32)
        painter = QtGui.QPainter(img)
        self.wb.mainFrame().render(painter)
        painter.end()
        logger.info('6')

        data = QtCore.QByteArray()
        buf = QtCore.QBuffer(data)
        img.save(buf, 'PNG')
        logger.info('7')
        file_like = cStringIO.StringIO(data.data())
        pil_img = Image.open(file_like)
        tempfile_io = StringIO.StringIO()
        pil_img.save(tempfile_io, format='PNG')
        logger.info('8')
        tb_image = ThebloqImage()
        tb_image.file = InMemoryUploadedFile(tempfile_io, None, 'order_point_img.png', 'image/png', tempfile_io.len, None)
        tb_image.save()
        logger.info('9')
        return tb_image

c = Capturer()

class imageTransHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        super(imageTransHandler, self).__init__(*args, **kwargs)

    def get(self):
        try:
            self.post()
        except:
            pass

    def post(self):
        dt = json.loads(self.request.body)

        logger.info(self.request.body)

        tb_img = c.capture(dt['html_txt'])

        logger.info(str(json.dumps({
            'id': tb_img.id
        })))

        self.write(str(json.dumps({
            'id': tb_img.id
        })))

class Command(BaseCommand):
    args = '[port_number]'
    help = 'image from html generator'
    option_list = BaseCommand.option_list + (
        optparse.make_option('-p',
                             '--port',
                             default='8899',
                             dest='port',
                             help='socket'),
    )

    def handle(self, *args, **options):
        urls=[
            (r'/', imageTransHandler),
        ]

        application = tornado.web.Application(urls, auto_reload=True)
        http_server = tornado.httpserver.HTTPServer(application)
        http_server.listen('8899')
        tornado.ioloop.IOLoop.instance().start()
