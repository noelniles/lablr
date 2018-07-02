#! /usr/bin/env python3
import argparse
import json
import os
import sys
import time
from functools import partial
from glob import glob

import cv2
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QObject
from PyQt5.QtCore import QRect
from PyQt5.QtCore import QRectF
from PyQt5.QtCore import QSize
from PyQt5.QtCore import QThread
from PyQt5.QtGui import QPen
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QPainter
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QFileDialog

from PyQt5.QtWidgets import QMainWindow

from roi import Ui_ROI
from canvas import Canvas
from common import cv2qimage

class ProcessWorker(QObject):
    from PyQt5.QtGui import QImage
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

class ROISelector(QObject, Ui_ROI):
    def __init__(self, files):
        super(ROISelector, self).__init__(None)
        self.mainwindow = QMainWindow()

        self.setupUi(self.mainwindow)

        self.image_list = files
        self.current_index = 170
        self.current_image_name = None

        self.mode = 'crop'
        self.set_icons()
        self.connect_buttons()
        self.previously_selected_button = self.crop_btn

        self.worker_thread = QThread(self.mainwindow)
        self.worker = ProcessWorker(self.image_list)
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.finished.connect(self.worker.deleteLater)
        self.worker_thread.started.connect(self.worker.work)
        self.worker.image_changed.connect(self.set_image)

        self.scene = Canvas(self.mainwindow)
        self.image_display.setScene(self.scene)
        self.set_initial_image()

        self.roi_selected = False

    def set_initial_image(self):
        self.scene.setImage(self.image_list[0])

    def connect_buttons(self):
        self.save_btn.clicked.connect(self.on_save)
        self.crop_btn.clicked.connect(self.on_crop)
        self.lines_btn.clicked.connect(self.on_lines)
        self.clear_btn.clicked.connect(self.on_clear)
        self.start_btn.clicked.connect(self.on_start)

        self.import_action.triggered.connect(self.on_import)
        self.export_action.triggered.connect(self.on_save)

    def on_clear(self):
        self.scene.clear()

    def on_import(self):
        filename, _ = QFileDialog.getOpenFileName(
            self.mainwindow, 'Import a region of interest', None, 'JSON(*.json)'
        )
        if not filename:
            return

        roi = None
        with open(filename, 'r') as fd:
            roi = json.load(fd)

        self.scene.draw_roi(roi)

        print('roi: ', roi)

    def on_save(self):
        print('saving')
        self.mode = 'save'
        self.scene.set_mode(self.mode)
        self.previously_selected_button.setEnabled(True)
        self.previously_selected_button = self.save_btn
        self.save_btn.setEnabled(False)
        graphics = self.scene.graphics_items()

        filename, _ = QFileDialog.getSaveFileName(
            self.mainwindow, 'Save region of interest', None, 'JSON(*.json)'
        )

        with open(filename, 'w') as fd:
            json.dump(graphics, fd)

        print('Saved region of interest to {}'.format(filename))

    def on_crop(self):
        print('cropping')
        self.mode = 'crop'
        self.scene.set_mode(self.mode)
        self.previously_selected_button.setEnabled(True)
        self.previously_selected_button = self.crop_btn
        self.crop_btn.setEnabled(False)
     
    def on_lines(self):
        print('drawing lines')
        self.mode = 'lines'
        self.scene.set_mode(self.mode)
        self.previously_selected_button.setEnabled(True)
        self.previously_selected_button = self.lines_btn
        self.lines_btn.setEnabled(False)

    def set_icons(self):
        save_icon = QIcon('icons/save.svg')
        crop_icon = QIcon('icons/crop.svg')
        line_icon = QIcon('icons/draw_lines.svg')
        reset_icon = QIcon('icons/reset.svg')
        start_icon = QIcon('icons/start.svg')
        self.save_btn.setIcon(save_icon)
        self.crop_btn.setIcon(crop_icon)
        self.lines_btn.setIcon(line_icon)
        self.clear_btn.setIcon(reset_icon)
        self.start_btn.setIcon(start_icon)

    def on_start(self):
        self.worker_thread.start()

    def wheelEvent(self, event):
        print('Wheeeeeeeeeeeel')

    def show(self):
        self.mainwindow.show()

    def enqueue(self, filename_list):
        self.image_list.extend(filename_list)
        self.current_image_name = self.image_list[self.current_index]

    @pyqtSlot(QImage)
    def set_image(self, img):
        pixmap = QPixmap.fromImage(img)
        self.scene.set_qimage(pixmap)
        #self.scene.setImage(self.current_image_name)
        
    def set_data_directory(self, path):
        self.url_bar.setText(path)


def cli():
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--input', type=str, help='path to the data directory', required=True)
    return ap.parse_args()

def main():
    args = cli()
    app = QApplication([])

    # Gather the files
    files = glob(args.input+'/*.jpg')

    selector = ROISelector(files)
    selector.set_data_directory(args.input)

    # Add the files to the selector
    #selector.enqueue(files)

    selector.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()