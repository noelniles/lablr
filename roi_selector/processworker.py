import cv2
from PyQt5.QtCore import QObject
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QImage

from common import cv2qimage
from common import subtract_background
from cropper import Cropper
from stabilizer import Stabilizer
from stabilizer_gcbpm import StabilizerGCPBM
from stabilizer import StabilizingMethods

class ProcessWorker(QObject):
    image_changed = pyqtSignal(QImage)

    def __init__(self, files):
        super(ProcessWorker, self).__init__(parent=None)
        self.file_list = files
        self.roi_selected = False
        self.stabilizer = StabilizerGCPBM()
        self.cropper = Cropper()
        self.prev = None

    def work(self):
        for f in self.file_list:
<<<<<<< HEAD
            img = cv2.imread(f, 0)
            stab = self.stabilizer.get_plane(img, 7)
            #crop = self.cropper.crop(img)
            #res = cv2qimage(crop, False)
            res = cv2qimage(stab, False)
=======
            img = cv2.imread(f)

            crop = self.cropper.crop(img)

            if self.prev is None:
                self.prev = crop.copy()
                continue
            
            self.prev = subtract_background(0.6, self.prev, crop)
            print('prev shape', self.prev.shape)
            res = cv2qimage(self.prev, False)
>>>>>>> 7ec8c7adaa543dff71e47b6142a77c05e9879ed3
            self.image_changed.emit(res)
            QThread.msleep(1)
