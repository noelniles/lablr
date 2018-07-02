import json

import cv2
import numpy as np

from common import sharpen
from common import find_harris_corners

class Stabilizer:
    def __init__(self):
        self.last_frame = None
        self.ms = []
        self.ref_corners = None
        self.skipped_files = 0

    def stabilize(self, img):
        copy = sharpen(img)

        if self.last_frame is None:
            self.last_frame = copy
            self.ref_corners = find_harris_corners(copy)
            return img

        offset_corners = find_harris_corners(copy)

        if self.ref_corners is None or offset_corners is None:
            self.skipped_files += 1
            print('Did not find any corners. Skipped ', self.skipped_files)
            print('ref corners: ', self.ref_corners)
            print('offset corner: ', offset_corners)
            return None

        print('shape orig: ', self.ref_corners.shape)
        print('shape offs: ', offset_corners.shape)
        xform = cv2.estimateRigidTransform(self.ref_corners.astype(np.uint8), offset_corners.astype(np.uint8), True)

        if xform is None:
            self.skipped_files += 1
            print('Did not estimate the transform. Skipped ', self.skipped_files)
            return None

        self.ms.append(xform.tolist()) 

        cols, rows = copy.shape
        print('Stabilizing.')
        self.ref_corners = offset_corners
        return cv2.warpAffine(img, xform, (rows, cols))

    def save(self, filename):
        with open(filename, 'w') as fd:
            json.dump(self.ms, fd)
        