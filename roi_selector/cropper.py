#! /usr/bin/env python3
import argparse
import json
import sys
from glob import glob

import cv2
import numpy as np


def cli():
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', type=str, required=True)
    ap.add_argument('-roi', type=str, required=True)
    return ap.parse_args()

def line_to_polygon(lines):
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

def crop(img, polygon):
    rect = cv2.boundingRect(polygon)
    x, y, w, h = rect
    print(rect)
    cropped = img[y:y+h, x:x+w].copy()

    polygon = polygon - polygon.min(axis=0)
    print('polygon: ', polygon)

    mask = np.zeros(cropped.shape[:2], np.uint8)
    cv2.drawContours(mask, [polygon.astype(int)], -1, (255, 255, 255), -1, cv2.LINE_AA)
    dst = cv2.bitwise_and(cropped, cropped, mask=mask)
    bg = np.ones_like(cropped, np.uint8) * 255
    cv2.bitwise_not(bg, bg, mask=mask)
    dst2 = bg + dst

    cv2.imshow('cropped', cropped)
    if cv2.waitKey(1) == ord('q'):
        cv2.destroyAllWindows()
        sys.exit(0)


def main():
    args = cli()
    files = glob(args.i+'/*.jpg')

    # Open the ROI
    with open(args.roi, 'r') as fd:
        points = json.load(fd)

    lines = points['lines']
    polygon = line_to_polygon(lines)

    for fn in files:
        img = cv2.imread(fn)
        if img is None:
            continue
        crop(img, polygon)

if __name__ == '__main__':
    main()