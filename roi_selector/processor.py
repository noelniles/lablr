#! /usr/bin/env python3
import argparse
import cv2
import json
import sys
from glob import glob

from common import adjust_gamma
from cropper import Cropper
from stabilizer import Stabilizer
from stabilizer import StabilizingMethods


class Processor:
    def __init__(self, files, roi):
        self.files = files
        self.cropper = Cropper(roi)
        self.stabilizer = Stabilizer(StabilizingMethods.GOOD_FEATURES)
        cv2.namedWindow('Results')

    def consume(self):
        for f in self.files:
            img = cv2.imread(f, 0)
            crop = self.cropper.crop(img)
            gamm = adjust_gamma(crop, gamma=2.0)
            stab = self.stabilizer.stabilize(gamm)

            if stab is None:
                continue
            cv2.imshow('Results', stab)

            if cv2.waitKey(1) == ord('q'):
                cv2.destroyAllWindows()
                sys.exit(0)

def cli():
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', type=str, required=True)
    ap.add_argument('-roi', type=str, required=True)
    return ap.parse_args()

def main():
    args = cli()
    files = glob(args.i+'/*.jpg')

    # Open the ROI
    with open(args.roi, 'r') as fd:
        points = json.load(fd)

    lines = points['lines']
    processor = Processor(files, lines)
    processor.consume()

if __name__ == '__main__':
    main()