import json
from enum import Enum

import cv2
import numpy as np

from common import sharpen
from common import find_harris_corners
from common import find_good_features
from common import optical_flow


class StabilizingMethods(Enum):
    HARRIS_CORNERS = find_harris_corners
    GOOD_FEATURES = find_good_features
    HARRIS_CORNERS_SUBPIX = 'NI'


class Stabilizer:
    def __init__(self):
        self.last_frame = None
        self.ms = []
        self.ref_corners = None
        self.skipped_files = 0
        #self.feature_finder = feature_finder

    def stabilize(self, img):
        #copy = sharpen(img)

        if self.last_frame is None:
            self.last_frame = img
            #self.ref_corners = self.feature_finder(copy)
            return img

        #offset_corners = self.feature_finder(copy)
        flowed = optical_flow(self.last_frame, img)
        self.last_frame = flowed
        return flowed

        #if self.ref_corners is None or offset_corners is None:
        #    self.skipped_files += 1
        #    print('Did not find any corners. Skipped ', self.skipped_files)
        #    print('ref corners: ', self.ref_corners)
        #    print('offset corner: ', offset_corners)
        #    return None

        #xform = cv2.estimateRigidTransform(self.ref_corners.astype(np.uint8), offset_corners.astype(np.uint8), True)

        #if xform is None:
        #    self.skipped_files += 1
        #    print('Did not estimate the transform. Skipped ', self.skipped_files)
        #    return None

        #self.ms.append(xform.tolist()) 

        #cols, rows = copy.shape
        #print('Stabilizing.')
        ##self.ref_corners = offset_corners
        #return cv2.warpAffine(img, xform, (rows, cols))

    def save(self, filename):
        with open(filename, 'w') as fd:
            json.dump(self.ms, fd)
        