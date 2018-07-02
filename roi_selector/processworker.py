import cv2
from PyQt5.QtCore import QObject
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QImage

from common import cv2qimage

class ProcessWorker(QObject):
    image_changed = pyqtSignal(QImage)

    def __init__(self, files):
        super(ProcessWorker, self).__init__(parent=None)
        self.file_list = files
        self.roi_selected = False

    def work(self):
        if not self.roi_selected:
            fn = self.file_list[0]

        for f in self.file_list:
            img = cv2.imread(f)
            img = cv2qimage(img, False)
            print('Working: ', img.width())
            self.image_changed.emit(img)
            QThread.msleep(1)
