#! /usr/bin/env python3
import argparse
import sys
from glob import glob

import cv2
import numpy as np
from skimage import io


def best_fit_transform(A, B):
    """Calculate the least-squares best-fit transform that maps points in A
    to corresponding points in B in m spatial dimensions.

    Arguments:
        A (ndarray): Nxm matrix of points
        B (ndarray): Nxm matrix of points
    Returns:
        T: (m+1)x(m+1) homogenous transformation matrix that maps A to B
        R: mxm rotation matrix
        t: m+1 translation matrix
    """
    assert A.shape == B.shape, "Arrays must be the same size. A={}, B={}".format(A.shape, B.shape)

    # Get the number of dimensions.
    m = A.shape[1]

    # Translate points to their centroids.
    centroid_A = np.mean(A, axis=0)
    centroid_B = np.mean(B, axis=0)
    AA = A - centroid_A
    BB = B - centroid_B

    # Get the rotation matrix.
    H = np.dot(AA.T, BB)
    U, S, Vt = np.linalg.svd(H)
    R = np.dot(Vt.T, U.T)

    # Special reflection case.
    if np.linalg.det(R) < 0:
        Vt[m-1,:] += -1
        R = np.dot(Vt.T, U.T)

    # Translation.
    t = centroid_B.T - np.dot(R, centroid_A.T)

    # Homogneous transformation.
    T = np.identity(m+1)
    T[:m, :m] = R
    T[:m, m] = t
    return T, R, t


def window(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    w, h = img.shape[:2]
    x, y = np.meshgrid(np.linspace(-1, 1, h), np.linspace(-1, 1, w))
    d = np.sqrt(x*x+y*y)
    sigma, mu = 1.0, 0.0
    g = np.exp(-((d-mu)**2 / (2.0 * sigma**2)))
    return np.uint8(g * img)


def cvdft(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = np.float32(img)
    dft = cv2.dft(img, flags=cv2.DFT_COMPLEX_OUTPUT)
    shift = np.fft.fftshift(dft)
    return np.log(shift, shift)

def cvdct(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rows, cols = img.shape[:2]
    nrows = cv2.getOptimalDFTSize(rows)
    ncols = cv2.getOptimalDFTSize(cols)
    padded = cv2.copyMakeBorder(img, 0, nrows - rows, 0, ncols - cols, cv2.BORDER_CONSTANT, value=[0,0,0])

    imf = np.float32(padded)
    dst = cv2.dct(imf)
    return np.uint8(dst) * 255.0


def spectrum_magnitude(img):
    # Pad image to optimal size.
    #img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rows, cols = img.shape[:2]
    nrows = cv2.getOptimalDFTSize(rows)
    ncols = cv2.getOptimalDFTSize(cols)
    padded = cv2.copyMakeBorder(img, 0, nrows - rows, 0, ncols - cols, cv2.BORDER_CONSTANT, value=[0,0,0])

    # Make space to complex and real values.
    planes = [np.float32(padded), np.zeros(padded.shape, np.float32)]
    Icomplex = cv2.merge(planes)

    # Make the DST
    dft = cv2.dft(Icomplex, Icomplex)

    # Transform real and complex values to magnitude.
    cv2.split(Icomplex, planes)
    cv2.magnitude(planes[0], planes[1], planes[0])
    Imag = planes[0]

    # Convert to log scale.
    ones = np.ones(Imag.shape, dtype=Imag.dtype)
    cv2.add(ones, Imag, Imag)
    cv2.log(Imag, Imag)

    Imag_rows, Imag_cols = Imag.shape
    Imag = Imag[0:Imag_rows & -2, 0:Imag_cols & -2]
    cx = int(Imag_rows/2)
    cy = int(Imag_cols/2)

    q0 = Imag[0:cx, 0:cy]       # Top left
    q1 = Imag[cx:cx+cx, 0:cy]   # Top right
    q2 = Imag[0:cx, cy:cy+cy]
    q3 = Imag[cx:cx+cx, cy:cy+cy]

    # Swap top left with bottom right.
    tmp = np.copy(q0)
    Imag[0:cx, 0:cy] = q3
    Imag[cx:cx+cx, cy:cy+cy] = tmp

    # Swap top right with bottom left.
    tmp = np.copy(q1)
    Imag[cx:cx+cx, 0:cy] = q2
    Imag[0:cx, cy:cy+cy] = tmp

    cv2.normalize(Imag, Imag, 0, 1, cv2.NORM_MINMAX)
    return Imag

def deshake_corners(ref, off):
    src = cv2.cornerHarris(np.float32(ref), 2, 3, 0.04)
    dst = cv2.cornerHarris(np.float32(off), 2, 3, 0.04)
    T, R, t = best_fit_transform(src, dst)
    print('T: ', T)
    print('R: ', R)
    print('t: ', t)
    return T

def find_peaks(img):
    """Find the peaks in the image."""

    peaks = cv2.minMaxLoc(img)
    print(peaks)
    return peaks

def detect(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = np.float32(gray)
    #corners = cv2.goodFeaturesToTrack(gray, 300, 0.01, 20, useHarrisDetector=True)
    corners = cv2.cornerHarris(gray, 2, 3, 0.05)
    corners = cv2.dilate(corners, None)
    ret, corners = cv2.threshold(corners, 0.01*corners.max(), 255, 0)

    corners = np.uint8(corners)

    #ret, labels, stats, centroids = cv2.connectedComponentsWithStats(corners)
    #criteria = (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
    #corners = cv2.cornerSubPix(gray, np.float32(centroids), (5,5), (-1,-1), criteria)
    return corners

    # Now draw them
    #res = np.hstack((centroids, corners))
    #res = np.int0(res)
    #img[res[:,1],res[:,0]]=[0,0,255]
    #:wimg[res[:,3],res[:,2]] = [0,255,0]

    #return img

def crop(img, r):
    return img[int(r[1]) : int(r[1] + r[3]),
               int(r[0]) : int(r[0] + r[2])]

def load_image(f):
    img = cv2.imread(f)
    img = cv2.resize(img, None, fx=0.25, fy=0.25)
    return img

def process(directory):
    img = cv2.imread(directory[0])
    img = cv2.resize(img, None, fx=0.25, fy=0.25)
    r = cv2.selectROI(img)
    roi = crop(img, r)

    #ref_corners = detect(roi)

    for fn in directory:
        img = cv2.imread(fn)
        img = cv2.resize(img, None, fx=0.25, fy=0.25)
        roi = crop(img, r)
        win = window(roi)
        mag = spectrum_magnitude(win)
        #corners = detect(roi)
        #xform = cv2.estimateRigidTransform(ref_corners, corners, True)

        #unshook = cv2.transform(np.float32(roi), xform)
        #s, c = cv2.split(unshook)
        res = cv2.resize(mag, None, fx=4.0, fy=4.0)
        cv2.imshow('Results', res)

        if cv2.waitKey(1) == ord('q'):
            sys.exit(0)
            cv2.destroyAllWindows()

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', type=str, required=True)
    cv2.namedWindow('Results')
    args = ap.parse_args()

    #files = io.ImageCollection(args.i+'/*.jpg', load_func=load_image)
    files = glob(args.i+'/*.jpg')
    process(files)

    #process(directory)
    #img = cv2.imread(args.i, 0)
    #img = cv2.resize(img, None, fx=0.25, fy=0.25)



    #img = crop(img, r)
    #corners = detect(img)

    #cv2.imshow('Results', corners)

    #if cv2.waitKey(0) == ord('q'):
    #    sys.exit(0)
