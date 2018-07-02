"""These are functions that are used all the time and don't care about 
what is happening in the outside world.
"""
import cv2
import numpy as np


def adjust_gamma(img, gamma=1.0):
    invgamma = 1.0 / gamma
    table = np.array([((i/255.0)**invgamma) * 255
        for i in np.arange(0,256)]).astype('uint8')

    return cv2.LUT(img, table)

def find_harris_corners(img):
    """Find the corners.

    Argument:
        img (ndarray): grayscale image
    Returns:
        dst (ndarry): a uint8 array
    """
    img = np.float32(img)
    dst = cv2.cornerHarris(img, 2, 3, 0.04)
    dst = cv2.dilate(dst, None)
    ret, dst = cv2.threshold(dst, 0.01*dst.max(), 255, 0)
    dst = np.uint8(dst)
    return dst

def equalize(img):
    nchannels = len(img.shape)
    if nchannels == 3:
        b, g, r = cv2.split(img)
        b = cv2.equalizeHist(b)
        g = cv2.equalizeHist(g)
        r = cv2.equalizeHist(r)
        return cv2.merge((b, g, r))
    else:
        return cv2.equalizeHist(img)

def sharpen(img):
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    return cv2.filter2D(img, -1, kernel)
