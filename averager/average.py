#! /usr/bin/env python
import argparse
import os
import sys
from glob import glob
from itertools import chain

import cv2
import numpy as np


def adjust_luminance(img):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl, a, b))
    return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

def gather_images(directory, patterns):
    return chain.from_iterable(glob(directory + '/' + e) for e in patterns)

def gamma_correct(img, gamma=2.2):
    igamma = 1 / gamma
    corrected = img**igamma
    #normalized = cv2.normalize(corrected, None, norm_type=cv2.NORM_MINMAX)
    return corrected

def brightness_contrast_adjust(img, gain=1, bias=0):
    adjusted = gain * (img + bias)
    #normalized = cv2.normalize(adjusted, None, norm_type=cv2.NORM_MINMAX)
    return adjusted

def average(files):
    first = cv2.imread(next(files))
    first = cv2.resize(first, None, fx=0.25, fy=0.25)
    first = adjust_luminance(first)
    first = cv2.cvtColor(first, cv2.COLOR_BGR2GRAY)
    n = 0

    Iavg = np.float64(first)
    beta = 10
    a = 0.5


    for fn in files:
        img = cv2.imread(fn)
        img = cv2.resize(img, None, fx=0.25, fy=0.25)
        img = adjust_luminance(img)
        cv2.imshow('Average', np.uint8(img))
        if cv2.waitKey(1) == ord('q'):
            cv2.destroyAllWindows()
            sys.exit(0)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        fimg = np.float64(img)
        #adj = brightness_contrast_adjust(fimg, gain=a, bias=beta)
        #gamma = gamma_correct(adj)
        cv2.accumulateWeighted(fimg, Iavg, alpha=0.8)
        n += 1

    Iavg = Iavg / n
    Iavg = cv2.normalize(Iavg, None, norm_type=cv2.NORM_MINMAX)
    return Iavg

def cli():
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--input_directory',
        type=str, required=True,
        help='input directory containing images to be averaged'
    )
    return ap.parse_args()

def main():
    extensions = ['*.jpg', '*.png']
    args = cli()
    files = gather_images(args.input_directory, extensions)

    Iavg = average(files)

    cv2.imshow('Average', Iavg)

    if cv2.waitKey(0) == ord('q'):
        cv2.destroyAllWindows()
        sys.exit(0)

if  __name__ == '__main__':
    main()