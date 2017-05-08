import numpy
import skimage
from skimage import data
import scipy
from scipy import misc

def rgb2yuv(rgb):
    """Function rgb2yuv converts given color from RGB color space in the
YUV color space."""
    if type(rgb) is numpy.ndarray:
        shape = rgb.shape
        height = shape[0]
        width = shape[1]
        yuv = numpy.zeros((height, width, 3))
        y = 0.299*rgb[:,:,0] + 0.587*rgb[:,:,1] + 0.114*rgb[:,:,2]
        u = 0.565*(rgb[:,:,2] - y)
        v = 0.713*(rgb[:,:,0] - y)
        yuv[:,:,0] = y
        yuv[:,:,1] = u
        yuv[:,:,2] = v
    else:
        yuv = "TODO"
    return yuv

def yuv2rgb(yuv):
    """Function yuv2rgb converts given color from YUV color space in the
RGB color space."""
    if type(yuv) is numpy.ndarray:
        shape = yuv.shape
        height = shape[0]
        width = shape[1]
        rgb = numpy.zeros((height, width, 3))
        r = yuv[:,:,0] + 1.403*yuv[:,:,2]
        g = yuv[:,:,0] - 0.433*yuv[:,:,1] - 0.714*yuv[:,:,2]
        b = yuv[:,:,0] + 1.770*yuv[:,:,1]
        rgb[:,:,0] = r
        rgb[:,:,1] = g
        rgb[:,:,2] = b
    else:
        rgb = "TODO"
    return rgb

moz = skimage.data.imread("monroe.jpg")
print moz
moz_grey = skimage.data.imread('monroepred.png', as_grey = True)
print moz_grey
yuv = rgb2yuv(moz)
yuv[:,:,0] = moz_grey
slika = yuv2rgb(yuv)
scipy.misc.imsave("proba.jpg", slika)
