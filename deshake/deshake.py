import argparse
import sys
from glob import glob

import cv2
import numpy as np


def spectrum_magnitude(img):
    # Pad image to optimal size.
    rows, cols = ref_img.shape
    nrows = cv2.getOptimalDFTSize(rows)
    ncols = cv2.getOptimalDFTSize(cols)
    padded = cv2.copyMakeBorder(ref_img, 0, nrows - rows, 0, ncols - cols, cv2.BORDER_CONSTANT, value=[0,0,0])

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
    Imad = Imag[0:Imag_rows & -2, 0:Imag_cols & -2]
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

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--input', type=str, required=True)
    args = ap.parse_args()

    files = sorted(glob(args.input+'/*.jpg'))

    ref_img = cv2.imread(files[0], 0)
    ref_img = cv2.resize(ref_img, None, fx=0.25, fy=0.25)

    print('ref_img', files[69])
    offset_img = cv2.imread(files[75], 0)
    offset_img = cv2.resize(offset_img, None, fx=0.25, fy=0.25)

    ref_mag = spectrum_magnitude(ref_img)
    offset_mag = spectrum_magnitude(offset_img)

    src = cv2.cornerHarris(np.float32(ref_img), 2, 5, 0.5)
    dst = cv2.cornerHarris(np.float32(offset_img), 2, 5, 0.5)
    xform = cv2.estimateRigidTransform(np.uint8(src), np.uint8(dst), True)
    print(xform)

    cv2.namedWindow('reference magnitude spectrum')
    cv2.namedWindow('offset magnitude spectrum')

    cv2.imshow('reference spectrum magnitude', ref_mag)
    cv2.imshow('offset magnitude spectrum', src)

    if cv2.waitKey(0) == ord('q'):
        cv2.destroyAllWindows()
        sys.exit()




