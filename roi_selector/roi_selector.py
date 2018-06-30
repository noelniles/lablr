#! /usr/bin/env python3
import argparse
import os
import sys
from functools import partial
from glob import glob

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import QRect
from PyQt5.QtCore import QRectF
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPen
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QPainter
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtWidgets import QMainWindow

from roi import Ui_ROI


class Canvas(QGraphicsScene):
    def __init__(self, parent=None):
        super(Canvas, self).__init__(parent)
        self.last_point = None
        self.is_drawing = False
        self.image = QImage()
        self.last_point = QPoint()
        self.modified = False
        
    def set_mode(self, mode):
        self.mode = mode

    def setImage(self, filename):
        self.pixmap = QPixmap(filename)
        self.addPixmap(self.pixmap)
        self.image = QImage(filename)

    def mouseMoveEvent(self, e):
        if e.buttons() & Qt.LeftButton and self.is_drawing:
            self.drawLineTo(e.pos())

    def mousePressEvent(self, e):
        print('pressed a button')
        if e.button() == Qt.LeftButton:
            self.last_point = e.pos()
            self.is_drawing = True

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton and self.is_drawing:
            self.drawLineTo(e.pos())
            self.is_drawing = False

    def paintEvent(self, e):
        painter = QPainter(self.image)
        painter.setRenderingHint(QPainter.Antialiasing)
        pen = QPen(Qt.red, 3)
        brush = 
        dirty_rect = e.rect()
        painter.drawImage(dirty_rect, self, dirty_rect)
        painter.end()

    def drawLineTo(self, endpoint):
        print('drawing a line')
        painter = QPainter(self.image)
        painter.setPen(QPen(Qt.red, 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawLine(self.last_point, endpoint)
        self.modified = True
        rad = 3 / 2 + 2
        self.update(QRectF(self.last_point, endpoint).normalized().adjusted(-rad, -rad, +rad, +rad))
        painter.end()
        self.last_point = QPoint(endpoint.toPoint())


class ROISelector(Ui_ROI):
    def __init__(self):
        self.mainwindow = QMainWindow()

        self.setupUi(self.mainwindow)

        self.image_list = []
        self.current_index = 170
        self.current_image_name = None
        self.scene = Canvas(self.mainwindow)

        self.image_display.wheelEvent = self.wheelEvent

        self.mode = 'crop'
        self.set_icons()
        self.connect_buttons()
        self.previously_selected_button = self.crop_btn

    def connect_buttons(self):
        self.save_btn.clicked.connect(self.on_save)
        self.crop_btn.clicked.connect(self.on_crop)
        self.lines_btn.clicked.connect(self.on_lines)

    def on_save(self):
        print('saving')
        self.mode = 'save'
        self.scene.set_mode(self.mode)
        self.previously_selected_button.setEnabled(True)
        self.previously_selected_button = self.save_btn
        self.save_btn.setEnabled(False)

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
        self.save_btn.setIcon(save_icon)
        self.crop_btn.setIcon(crop_icon)
        self.lines_btn.setIcon(line_icon)

    def wheelEvent(self, event):
        print('Wheeeeeeeeeeeel')

    def show(self):
        self.set_image()
        self.mainwindow.show()

    def enqueue(self, filename_list):
        self.image_list.extend(filename_list)
        self.current_image_name = self.image_list[self.current_index]

    def set_image(self):
        print('current image name: ', self.current_image_name)
        self.scene.setImage(self.current_image_name)
        self.image_display.setScene(self.scene)
        
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

    selector = ROISelector()
    selector.set_data_directory(args.input)

    # Add the files to the selector
    selector.enqueue(files)

    selector.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()