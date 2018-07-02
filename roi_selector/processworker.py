import cv2
from PyQt5.QtCore import QObject
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QImage

from common import cv2qimage
from common import subtract_background
from cropper import Cropper
from stabilizer import Stabilizer
from stabilizer import StabilizingMethods

class ProcessWorker(QObject):
    image_changed = pyqtSignal(QImage)

    def __init__(self, files):
        super(ProcessWorker, self).__init__(parent=None)
        self.file_list = files
        self.roi_selected = False
        self.stabilizer = Stabilizer()
        self.cropper = Cropper()
        self.prev = None

    def work(self):
        for f in self.file_list:
            img = cv2.imread(f)

            crop = self.cropper.crop(img)

            if self.prev is None:
                self.prev = crop.copy()
                continue
            
            self.prev = subtract_background(0.2, self.prev, crop)
            print('prev shape', self.prev.shape)
            res = cv2qimage(self.prev, False)
            self.image_changed.emit(res)
            #QThread.msleep(1)
