import sys
from PyQt4 import QtCore, QtGui, QtWebKit
from django.core.files.uploadedfile import InMemoryUploadedFile
import cStringIO
import StringIO
from PIL import Image
from lugati.lugati_media.models import ThebloqImage
import time

app = QtGui.QApplication(['lugati'])

class Capturer(QtCore.QObject):
    ready_trigger = QtCore.pyqtSignal()
    finish_trigger = QtCore.pyqtSignal()
    loop = QtCore.QEventLoop()
    def __init__(self, url='', filename='kde.png'):
        super(Capturer, self).__init__()
        self.url = url
        self.filename = filename
        self.saw_initial_layout = False
        self.saw_document_complete = False
        self.wb = QtWebKit.QWebPage()
        self.wb.loadFinished.connect(self.loadFinishedSlot)
        self.wb.mainFrame().initialLayoutCompleted.connect(self.initialLayoutSlot)
        self.wb.mainFrame().setScrollBarPolicy(
            QtCore.Qt.Horizontal, QtCore.Qt.ScrollBarAlwaysOff)
        self.wb.mainFrame().setScrollBarPolicy(
            QtCore.Qt.Vertical, QtCore.Qt.ScrollBarAlwaysOff)

    def loadFinishedSlot(self):
        print 'load finished'
        self.saw_document_complete = True
        if self.saw_initial_layout and self.saw_document_complete:
            self.ready_trigger.emit()
            # self.doCapture()

    def initialLayoutSlot(self):
        print 'initial layout'
        self.saw_initial_layout = True
        if self.saw_initial_layout and self.saw_document_complete:
            self.ready_trigger.emit()
            # self.doCapture()

    def capture(self, html_str):

        # f = open('/home/xors/workspace/pycharm/lugati_e_commerce/lugati_html_str.txt', 'r')
        # st = f.read()
        # f.close()



        self.wb.mainFrame().setHtml(html_str)
        while not (self.saw_initial_layout and self.saw_document_complete):
            self.loop.processEvents()
            pass
        self.saw_initial_layout = False
        self.saw_document_complete = False
        # self.ready_trigger.connect(self.loop.exit)
        # self.loop.exec_()
        # while not self.wb.isModified():
        #     pass
        self.wb.setViewportSize(self.wb.mainFrame().contentsSize())
        img = QtGui.QImage(self.wb.viewportSize(), QtGui.QImage.Format_ARGB32)
        painter = QtGui.QPainter(img)
        self.wb.mainFrame().render(painter)
        painter.end()

        data = QtCore.QByteArray()
        buf = QtCore.QBuffer(data)
        img.save(buf, 'PNG')

        file_like = cStringIO.StringIO(data.data())
        pil_img = Image.open(file_like)
        tempfile_io = StringIO.StringIO()
        pil_img.save(tempfile_io, format='PNG')

        tb_image = ThebloqImage()
        tb_image.file = InMemoryUploadedFile(tempfile_io, None, 'order_point_img.png', 'image/png', tempfile_io.len, None)
        # tb_image.content_object = new_prod
        tb_image.save()
        # QtCore.QCoreApplication.instance().quit()
        return tb_image
    # def lugati_close(self):
    #     QtCore.QCoreApplication.instance().quit()

# app.exec_()
# capturer = Capturer()

def get_img(html_str):

    # capturer = Capturer()
    # img = capturer.capture(html_str)
    # capturer.lugati_close()
    return img
