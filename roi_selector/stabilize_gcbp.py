import cv2
import numpy as np


def make_bit_plane(src, bit):
    if bit > 7: bit = 7
    if bit < 0: bit = 0
    print('making bit plane')
    w, h = src.shape[:2]
    dst = np.zeros((w, h, 1), np.uint8)
    for y in range(h):
        print('outer loop')
        for x in range(w):
            current_bit = (src[x:y] >> 7) & 1

            for i in reversed(range(bit, 6)):
                print(current_bit)
                current_bit ^= (src.at[x:y] >> i) & 1
                dst[x:y] = current_bit

    return dst
