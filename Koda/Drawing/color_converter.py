import numpy

# rgb2yuv -------------------------------------------------------------#
def rgb2yuv(rgb):
    """ """
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
    return yuv

# yuv2rgb -------------------------------------------------------------#
def yuv2rgb(yuv):
    """ """
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
    return rgb

import numpy
import skimage
from skimage import data
import scipy
from scipy import misc


moz = skimage.data.imread("bogensperk.jpg")
print moz
moz_grey = skimage.data.imread('bg1.jpg', as_grey = True)
print moz_grey
yuv = rgb2yuv(moz)
yuv[:,:,0] = moz_grey
slika = yuv2rgb(yuv)
scipy.misc.imsave("bogenproba.jpg", slika)

