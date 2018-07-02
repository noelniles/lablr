"""These are functions that are used all the time and don't care about 
what is happening in the outside world.
"""
import cv2
import numpy as np
from PyQt5.QtGui import qRgb
from PyQt5.QtGui import QImage

gray_color_table = [qRgb(i, i, i) for i in range(256)]

def cv2qimage(img, copy=False):
    if img is None:
        return QImage()

    if img.dtype == np.uint8:
        if len(img.shape) == 2:
            qimg = QImage(img.data, img.shape[1], img.shape[0], img.strides[0], QImage.Format_Indexed8)
            qimg.setColorTable(gray_color_table)
            return qimg.copy() if copy is True else qimg

        elif len(img.shape) == 3:
            if img.shape[2] == 3:
                qimg = QImage(img.data, img.shape[1], img.shape[0], img.strides[0], QImage.Format_RGB888)
                return qimg.copy() if copy is True else qimg
            elif img.shape[2] == 4:
                qimg = QImage(img.data, img.shape[1], img.shape[0], img.strides[0], QImage.Format_ABGR32)
                return qimg.copy if copy else qimg

def warp_flow(img, flow):
    h, w = flow.shape[:2]
    flow = -flow
    flow[:,:,0] += np.arange(w)
    flow[:,:,1] += np.arange(h)[:,np.newaxis]
    return cv2.remap(img, flow, None, cv2.INTER_LINEAR)

def adjust_gamma(img, gamma=1.0):
    invgamma = 1.0 / gamma
    gamma_table = np.array([((i/255.0)**invgamma) * 255
        for i in np.arange(0,256)]).astype('uint8')
    return cv2.LUT(img, gamma_table)

def optical_flow(prev, curr):
    flow = cv2.calcOpticalFlowFarneback(prev, curr, None, 0.8, 3, 5, 3, 5, 1.2, 0)
    return warp_flow(curr, flow)

def find_good_features(img):
    corners = cv2.goodFeaturesToTrack(img, 25, 0.01, 10)
    corners = np.uint8(corners)
    return corners
    
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
