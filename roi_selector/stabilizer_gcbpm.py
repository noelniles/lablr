import numpy as np
import matplotlib.pyplot as plt


class StabilizerGCPBM:
    def __init__(self):
        pass


    def get_plane(self, gray, n):
        planes = []
        
        width, height = gray[:2]
        mask = np.ones((width, height), np.uint8)
        for i in range(8):
            out = np.bitwise_and(gray/2, mask)
            out *= 255
            planes.append(out)

        return planes[n]

        
