#! /usr/bin/env python3
import json
import math
import sys
from glob import glob
from queue import Queue
from threading import Thread

import cv2
import numpy as np

class Cropper:
    def __init__(self):
        self.roi = None
        self.rect = None

    def add_roi(self, roi):
        self.roi = roi
        self.polygon = self.lines_to_polygon(roi)
        self.rect = cv2.boundingRect(self.polygon)

    def crop(self, img):
        if self.roi is None or img is None:
            return
        rect = self.rect
        x, y, w, h = rect
        return img[y:y+h, x:x+w].copy()

    def lines_to_polygon(self, lines):
        pts = np.array(lines).T
        
        res = np.array([])

        left = []
        right = []
        points = []
        for x, y, in zip(pts[0], pts[1]):
            left.append([x, y])

        for x, y in zip(pts[2], pts[3]):
            right.append([x, y])

        points.extend(left)
        points.extend(right)
        return np.array(points, dtype=np.float32)