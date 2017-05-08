# -*- coding: cp1250 -*-
import numpy
import skimage
from skimage import data
from skimage import segmentation
import cairo
import sys
import scipy

class Segmentation():
    
    # ---------------------------------------------------------------- #
    def __init__(self, file):
        self.file = file
        self.produce()

    def produce(self):
        try:
            self.source = skimage.data.imread(self.file, as_grey = True)
        except:
            print "can't load " + self.file
            sys.exit()
        # Size of source ndarray.
        shape = self.source.shape
        self.height = shape[0]
        self.width = shape[1]
        self.source = skimage.filter.gaussian_filter(self.source, 1)
        data = skimage.segmentation.felzenszwalb(self.source, scale=10, sigma=2, min_size=100)
        self.reduce_grey()
        self.color()

    def reduce_grey(self):
        k = 1./8
        for i in range(self.height):
            for j in range(self.width):
                self.source[i][j] = (self.source[i][j]//k)*k

    def color(self):
        self.color = numpy.zeros((self.height, self.width, 3))
        color_list = {}
        k = 8
        for c in numpy.linspace(0,1,k+1,endpoint=True):
            color_list[str(c)] = numpy.random.rand(3)
        for i in range(self.height):
            for j in range(self.width):
                self.color[i][j][:] = color_list[str(self.source[i][j])]
        scipy.misc.imsave("segmentcolor.jpg", self.color)

Segmentation("monroe2.jpg")
