#! /usr/bin/env python3
import argparse
import csv
import os
import sys
from glob import glob

import cv2
import numpy as np
from matplotlib import pyplot as plt

from filename_utils import date_from_filename
from filename_utils import get_camera_name


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

    return round((nonzero / size) * 100, 3)

def record(filename, datum):
    try:
        with open(filename, 'a') as f:
            writer = csv.writer(f, delimiter=' ')
            writer.writerow(datum)
    except FileNotFoundError:
        with open(filename, 'w') as f:
            writer = csv.writer(f, delimiter=' ')
            writer.writerow('index', 'filename', 'datetime', 'percent_sand', 'mask')
            writer.writerow(datum)

def write_thumb(directory, img, prefix):
    if not os.path.exists(directory):
        os.makedirs(directory)

    index = str(prefix).zfill(8)
    thumb_name = os.path.join(directory, '{}.jpg'.format(index))

    if not cv2.imwrite(thumb_name, img):
        print('Failed to write ', thumb_name)

    return thumb_name

def measure_sand(img):
    # Compute the beach percentage.
    beach = filter_by_color(img)
    res = cv2.cvtColor(beach, cv2.COLOR_HSV2BGR)
    return (res, measure(res))

def process(files, csv, thumbs=None):
    fps = 30.0
    font = cv2.FONT_HERSHEY_DUPLEX
    im = cv2.imread(files[10])
    im = cv2.resize(im, None, fx=0.25, fy=0.25)
    x, y, w, h = cv2.selectROI(im)

    # Set up the recording process.
    n = 0
    prefix = get_camera_name(os.path.basename(files[0])) + '-'
    suffix = '.jpg'

    for fn in files:
        f = os.path.basename(fn)

        # Get the date of this file.
        dt = date_from_filename(prefix, suffix, f)

        # Read and crop the image.
        im = cv2.imread(fn)
        im = cv2.resize(im, None, fx=0.25, fy=0.25)
        cropped = im[y:y+h, x:x+w]

        res, percentage_beach = measure_sand(cropped)

        # Enlarge the cropped region.
        res = cv2.resize(res, None, fx=4, fy=4)
        resw, resh = res.shape[:2]
        text_offset = (resw//2, 90)

        # Record the data.
        thumb_name = write_thumb(thumbs, res, n)
        datum = [n, fn, dt, percentage_beach, thumb_name]
        record(csv, datum)

        # Show the results.
        cv2.putText(res, '{:.2f}% sand'.format(percentage_beach), text_offset, font, 2, (0, 0, 255), 2)
        cv2.imshow('Results', res)
        cv2.imshow('Original', im)

        if cv2.waitKey(1) == ord('q'):
            sys.exit(0)
            cv2.destroyAllWindows()

        # Increment the frame counter.
        n += 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', type=str, required=True)
    ap.add_argument('-csv', type=str, required=True)
    ap.add_argument('-thumb', type=str)
    ap.add_argument('-n', type=int, help='number of frames to process')

    args = ap.parse_args()

    files = glob(args.i+'/*.jpg')
    camera_name = get_camera_name(files[0])
    csv_basename = camera_name + '-results.csv'
    csv_filename = args.csv
    cv2.namedWindow('Results')

    thumbs_directory = args.thumb
    process(files[0:args.n], csv_filename, thumbs_directory)

if __name__ == '__main__':
    main()

    