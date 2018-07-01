#! /usr/bin/env python3
import argparse
import json
import math
import os
import sys
import time
from functools import partial
from glob import glob

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QLineF
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import QPointF
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
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QGraphicsLineItem
from PyQt5.QtWidgets import QGraphicsEllipseItem
from PyQt5.QtWidgets import QGraphicsPixmapItem
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtWidgets import QMainWindow

from roi import Ui_ROI


class Canvas(QGraphicsScene):
    def __init__(self, parent=None):
        super(Canvas, self).__init__(parent)
        self.pen = QPen(Qt.red, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        self.last_point = None
        self.is_drawing = False
        self.image = QImage()
        self.last_point = QPoint()
        self.modified = False
        self.mode = 'crop'

        self.transect_points = []
        self.transect_lines = []
        self.npoints = lambda: len(self.transect_points)

        self.control_point_radius = 10
        
    def set_mode(self, mode):
        self.mode = mode

    def setImage(self, filename):
        self.pixmap = QPixmap(filename)
        self.addPixmap(self.pixmap)
        self.image = QImage(filename)

    def mouseMoveEvent(self, e):
        if e.buttons() & Qt.LeftButton and self.is_drawing:
            pass

    def mousePressEvent(self, e):
        pos = e.scenePos()
        if e.button() == Qt.LeftButton:
            if self.mode == 'lines':
                if self.point_exists(pos):
                    self.remove_control_point(pos)
                self.draw_control_point(pos)
            self.last_point = pos
            self.is_drawing = True

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton and self.is_drawing:
            self.is_drawing = False

    #def paintEvent(self, e):
    #    painter = QPainter(self.image)
    #    painter.setRenderHint(QPainter.Antialiasing)
    #    pen = QPen(Qt.red, 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    #    painter.setPen(pen)
    #    dirty_rect = e.rect()
    #    painter.drawImage(dirty_rect, self, dirty_rect)
    #    painter.end()

    def draw_control_point(self, pos):
        point = QPointF(pos)
        self.transect_points.append(point)
        x = pos.x()
        y = pos.y()
        r = self.control_point_radius

        self.addEllipse(x, y, r, r, self.pen)

        if not self.npoints() & 1:
            # We have an even number of points so draw the latest line.
            self.draw_latest_line()

        self.update()

    def point_exists(self, pos):
        if self.npoints() == 0:
            return

        epsilon = 5
        prev_pos = self.transect_points[self.npoints()-1]
        x1 = pos.x()
        x2 = prev_pos.x()
        y1 = pos.y()
        y2 = prev_pos.y()

        dx = x1 - x2
        dy = y1 - y2
        distance = math.sqrt(dx**2 + dy**2)

        if distance < epsilon:
            self.remove_control_point(prev_pos)

    def remove_control_point(self, pos):
        self.removeItem(self.transect_points[self.npoints()-1])

    def draw_latest_line(self):
        index = self.npoints() - 1
        r = self.control_point_radius / 2
        x1 = self.transect_points[index].x() + r
        x2 = self.transect_points[index-1].x() + r
        y1 = self.transect_points[index].y() + r 
        y2 = self.transect_points[index-1].y() + r
        print('latest line: ({}, {}), ({}, {})'.format(x1, y1, x2, y2))
        line = QLineF(x1, y1, x2, y2)
        self.transect_lines.append(line)
        self.addLine(line, self.pen)


    def drawLineTo(self, endpoint):
        print('drawing a line')
        self.modified = True
        #self.update(QRectF(self.last_point, endpoint).normalized().adjusted(-rad, -rad, +rad, +rad))
        self.last_point = QPoint(endpoint.toPoint())

    def graphics_items(self):
        items = self.items()

        lines = []
        ellipses = []

        for item in items:
            tp = type(item)
            if tp == QGraphicsEllipseItem:
                # save the ellipse.
                rect = item.rect()

                ellipses.append((rect.x(), rect.y(), rect.width(), rect.height()))
                print('ellipse')
            elif tp == QGraphicsLineItem:
                line = item.line()

                lines.append((line.x1(), line.y1(), line.x2(), line.y2()))
                # save the line.
                print('line')
            elif tp == QGraphicsPixmapItem:
                print('pixmap')
                # do something with the pixmap.

        return {'lines': lines, 'ellipses': ellipses}
            

class ROISelector(Ui_ROI):
    def __init__(self):
        self.mainwindow = QMainWindow()

        self.setupUi(self.mainwindow)

        self.image_list = []
        self.current_index = 170
        self.current_image_name = None
        self.scene = Canvas(self.mainwindow)

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
        graphics = self.scene.graphics_items()

        home = os.path.expanduser('~')
        settings_path = os.path.join(home, '.ibeach/roi')
        filename, _ = QFileDialog.getSaveFileName(
            self.mainwindow, 'Save region of interest', settings_path, 'JSON(*.json)')

        with open(filename, 'w') as fd:
            json.dump(graphics, fd)

        print('Saved region of interest to {}'.format(filename))



        print('filename', filename)

        print('graphics: ', graphics)

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
        self.mainwindow.setWindowTitle(
            'Select a region of interest: ' + os.path.basename(self.current_image_name))
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