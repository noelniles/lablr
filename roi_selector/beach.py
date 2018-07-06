#! /usr/bin/env python3
import argparse
import sys
from glob import glob

import cv2
import numpy as np
from matplotlib import pyplot as plt


def filter_by_color(img):
    """Finds colors within a certain range.
    
    Args
    img (ndarray): a BGR image

    Returns:
    masked (ndarray): hsv & coating_area_mask
    cls        (str): the class to filter e.g. 'dragx', 'corrosion', etc.
    """
    lo = np.array([10, 20, 10])
    hi = np.array([20, 255, 255])
    img = cv2.GaussianBlur(img.copy(), (3, 3), 0)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lo, hi)
    return cv2.bitwise_and(hsv, hsv, mask=mask)


def measure(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    w, h = img.shape[:2]
    size = w*h
    nonzero = cv2.countNonZero(gray)

    return nonzero / size


def process(files):
    fps = 30.0
    font = cv2.FONT_HERSHEY_DUPLEX
    im = cv2.imread(files[10])
    im = cv2.resize(im, None, fx=0.25, fy=0.25)
    #r = cv2.selectROI(im)

    #mask = np.zeros(im.shape[:2], np.uint8)
    #mask[r[1]: r[1]+r[3], r[0]:r[0]+r[2]] = 255
    #masked_image = cv2.bitwise_and(im, im, mask=mask)
    #hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    #hue, _, v = cv2.split(hsv)
    #hist = cv2.calcHist([hue], [0], mask, [256], [0, 256])

    #plt.hist(im.ravel(), 256, [0, 256])
    #plt.subplot(221)
    #plt.imshow(im)
    #plt.subplot(222)
    #plt.imshow(mask)
    #plt.subplot(223)
    #plt.imshow(masked_image)
    #plt.subplot(224)
    #plt.plot(hist)
    #plt.show()

    x, y, w, h = cv2.selectROI(im)
    print('x: {}, y:{}, w:{}, h:{}'.format(x, y, w, h))

    for fn in files:
        im = cv2.imread(fn)
        im = cv2.resize(im, None, fx=0.25, fy=0.25)
        cropped = im[y:y+h, x:x+w]

        beach = filter_by_color(cropped)

        res = cv2.cvtColor(beach, cv2.COLOR_HSV2BGR)
        res = cv2.resize(res, None, fx=4, fy=4)
        resw, resh = res.shape[:2]
        percentage_beach = measure(res)
        text_offset = (resw//2, 90)
        cv2.putText(res, '{:.2}% sand'.format(percentage_beach), text_offset, font, 2, (0, 0, 255), 2)
        cv2.imshow('Results', res)

        if cv2.waitKey(1) == ord('q'):
            sys.exit(0)
            cv2.destroyAllWindows()


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', type=str, required=True)
    args = ap.parse_args()

    files = glob(args.i+'/*.jpg')
    cv2.namedWindow('Results')
    process(files)

    