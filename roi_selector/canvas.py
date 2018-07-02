import math

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QPen
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import QPointF
from PyQt5.QtCore import QLineF
from PyQt5.QtWidgets import QGraphicsLineItem
from PyQt5.QtWidgets import QGraphicsEllipseItem
from PyQt5.QtWidgets import QGraphicsPixmapItem



class Canvas(QGraphicsScene):
    def __init__(self, parent=None):
        super(Canvas, self).__init__(parent)
        self.pen = QPen(Qt.red, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        self.last_point = None
        self.is_drawing = False
        self.image = QImage()
        self.pixmap_item = QGraphicsPixmapItem()
        self.addItem(self.pixmap_item)
        self.last_point = QPoint()
        self.modified = False
        self.mode = 'crop'

        self.transect_points = []
        self.transect_lines = []
        self.npoints = lambda: len(self.transect_points)

        self.control_point_radius = 10
        
    def set_mode(self, mode):
        self.mode = mode

    def set_qimage(self, qimage):
        self.pixmap_item.setPixmap(qimage)

    def setImage(self, filename):
        pixmap = QPixmap(filename)
        self.pixmap_item.setPixmap(pixmap)
        #self.addItem(self.pixmap_item)
        #self.image = QImage(filename)

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

    def draw_roi(self, roi):
        lines = roi['lines']
        for x1, y1, x2, y2, in lines:
            line = QLineF(x1, y1, x2, y2)
            self.transect_lines.append(line)
            self.addLine(line, self.pen)

    def clear(self):
        for item in self.items():
            tp = type(item)
            if tp is QGraphicsEllipseItem or tp is QGraphicsLineItem:
                self.removeItem(item)
            