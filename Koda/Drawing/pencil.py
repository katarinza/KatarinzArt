# -*- coding: utf8 -*-
# Imported libraries:
import scipy
import PIL
from PIL import Image
from scipy import signal
from scipy import ndimage
from scipy.misc import toimage
import skimage
from skimage import filter
from skimage import data
import math
from cv2 import fastNlMeansDenoisingColored, imread
import numpy
# My functions:
from histogram import histogram_transform
from color_converter import rgb2yuv, yuv2rgb
########################################################################
class PencilDrawing():

    def __init__(self, k=4, luminance=True, denoised=True, h=10, hColor=10):
        self.k = k
        self.luminance = luminance
        self.denoised = False
        self.h = h
        self.hColor = hColor
    # -----------------------------------------------------------------#
    def draw(self, file):
        # Algorithm.
        self.sketch(file) # part 1: lines
        self.tone_image(file) # part 2: tone
        self.combine() # pencil drawing
        self.color(file) # colored drawing
    # -----------------------------------------------------------------#
    def sketch(self, file):
        # Read file and save returned ndarray in source.
        # We remove noise from image, using fastNlMeansDenoisingColor from cv2.
        if self.denoised:
            img = skimage.data.imread(file)
            source_c = fastNlMeansDenoisingColored(img, h=self.h, hColor=self.hColor)
        else:
            source_c = skimage.data.imread(file)
        # We compute gray/luminance image.
        if self.luminance:
            source = 0.3*source_c[:,:,0] + 0.59*source_c[:,:,1] + 0.11*source_c[:,:,2]
        else:
            source = 0.33*source_c[:,:,0] + 0.33*source_c[:,:,1] + 0.33*source_c[:,:,2]
        # Dimensions:
        shape = source.shape
        self.height = shape[0]
        self.width = shape[1]
        # We compute gradients in x and y directions.
        gradient = numpy.gradient(source)
        (grad_x, grad_y) = gradient
        magnitude = numpy.hypot(grad_x, grad_y)
        # Algorithm.
        self.set_kernels()
        self.set_response_maps(magnitude)
        self.set_classification()
        self.set_lines()
        # Map.
        m = numpy.max(self.s_lines)
        self.s = 256 - (self.s_lines/m)*256
        scipy.misc.imsave("s.jpg", self.s)
    # -----------------------------------------------------------------#
    def set_kernels(self):
        self.kernels = {}
        size_k = 10
        size = 2*size_k + 1
        # Line 0°
        K1 = numpy.zeros((size, size))
        index_i, index_j = numpy.indices(K1.shape)
        K1[index_i == size_k] = 1
        K1 = (1./numpy.sum(K1))*K1
        self.kernels["K1"] = K1
        # Line 20°
        K2 = numpy.zeros((size, size))
        k = size - 1
        for i in range(size_k/2 + 1, size_k):
            K2[i, k-2 : k] = 1
            k = k - 2
        k = k - 1
        for i in range(size_k + 1, size_k + size_k/2 + 1):
            K2[i, k-2 : k] = 1
            k = k - 2
        K2[size_k + size_k/2 + 1, 0] = 1
        K2[size_k/2, size - 1] = 1
        K2[size_k, size_k] = 1
        K2 = (1./numpy.sum(K2))*K2
        self.kernels["K2"] = K2
        # Line 45°
        K3 = numpy.zeros((size, size))
        K3[index_i == size - index_j - 1] = 1
        K3 = (1./numpy.sum(K3))*K3
        self.kernels["K3"] = K3
        # Line 70°
        K4 = numpy.zeros((size, size))
        k = size - 1
        for i in range(size_k/2 + 1, size_k):
            K4[k-2 : k, i] = 1
            k = k - 2
        k = k - 1
        for i in range(size_k + 1, size_k + size_k/2 + 1):
            K4[k-2 : k, i] = 1
            k = k - 2
        K4[0, size_k + size_k/2 + 1] = 1
        K4[size - 1, size_k/2] = 1
        K4[size_k, size_k] = 1
        K4 = (1./numpy.sum(K4))*K4
        self.kernels["K4"] = K4
        # Line 90°
        K5 = numpy.zeros((size, size))
        K5[index_j == size_k] = 1
        K5 = (1./numpy.sum(K5))*K5
        self.kernels["K5"] = K5
        # Line 110°
        K6 = numpy.zeros((size, size))
        k = 1
        for i in range(size_k/2 + 1, size_k):
            K6[k : k+2, i] = 1
            k = k + 2
        k = k + 1
        for i in range(size_k + 1, size_k + size_k/2 + 1):
            K6[k : k+2, i] = 1
            k = k + 2
        K6[0, size_k/2] = 1
        K6[size - 1, size_k + size_k/2 + 1] = 1
        K6[size_k, size_k] = 1
        K6 = (1./numpy.sum(K6))*K6
        self.kernels["K6"] = K6
        # Line 135°
        K7 = numpy.zeros((size, size))
        K7[index_i == index_j] = 1
        K7 = (1./numpy.sum(K7))*K7
        self.kernels["K7"] = K7
        # Line 160°
        K8 = numpy.zeros((size, size))
        k = 1
        for i in range(size_k/2 + 1, size_k):
            K8[i, k : k+2] = 1
            k = k + 2
        k = k + 1
        for i in range(size_k + 1, size_k + size_k/2 + 1):
            K8[i, k : k+2] = 1
            k = k + 2
        K8[size_k/2, 0] = 1
        K8[size_k + size_k/2 + 1, size - 1] = 1
        K8[size_k, size_k] = 1
        K8 = (1./numpy.sum(K8))*K8
        self.kernels["K8"] = K8
    # ------------------------------------------------------------------
    def set_response_maps(self, magnitude):
        self.response_maps = {}
        i = 0
        for key, K in self.kernels.iteritems():
            G = scipy.signal.convolve2d(magnitude, K, 'same')
            self.response_maps[key] = G
            i = i + 1
    # ------------------------------------------------------------------
    def set_classification(self):
        max_value = reduce(numpy.maximum,
                           [self.response_maps["K1"],self.response_maps["K2"],
                            self.response_maps["K3"],self.response_maps["K4"],
                            self.response_maps["K5"],self.response_maps["K6"],
                            self.response_maps["K7"],self.response_maps["K8"]])
        self.classification = {}
        i = 0
        for key, G in self.response_maps.iteritems():
            Z = numpy.zeros((self.height, self.width))
            compare = numpy.equal(max_value, G)
            C = numpy.where(compare, G, Z)
            self.classification[key] = C
            i = i + 1
    # ------------------------------------------------------------------
    def set_lines(self):
        i = 0
        self.s_lines = numpy.zeros((self.height, self.width))
        for key, C in self.classification.iteritems():
            S = scipy.signal.convolve2d(C, self.kernels[key], 'same')
            self.classification[key] = S
            i = i + 1
            self.s_lines = self.s_lines + S
        self.s_lines = self.s_lines/8.
    # ------------------------------------------------------------------
    def tone_image(self, file):
        # Read file and save returned ndarray in source.
        source_c = skimage.data.imread(file)
        # We compute gray/luminance image.
        if self.luminance:
            source = 0.3*source_c[:,:,0] + 0.59*source_c[:,:,1] + 0.11*source_c[:,:,2]
        else:
            source = 0.33*source_c[:,:,0] + 0.33*source_c[:,:,1] + 0.33*source_c[:,:,2]
        shape = source.shape
        self.height = shape[0]
        self.width = shape[1]
        # Transformation.
        self.t = histogram_transform(source, self.width, self.height)
        scipy.misc.imsave("risbicat.jpg", self.t)
    # ------------------------------------------------------------------
    def combine(self):
        tone = self.t
        line = self.s
        self.effect = numpy.multiply(tone, line)
        scipy.misc.imsave("risbicat.png", self.t)
        scipy.misc.imsave("risbicas.jpg", self.s)
        scipy.misc.imsave("risbica.jpg", self.effect)
        tekstura = skimage.data.imread("tekstura.png", as_grey=True)
        shape = tekstura.shape
        h = shape[0]
        w = shape[1]
        n = 256*(256*tekstura*tone[0:h,50:50+w])/numpy.max((256*tekstura*tone[0:h,0:w]))
        tone[0:h,450:450+w] = n
        scipy.misc.imsave("tekst.jpg", tone)
    # ------------------------------------------------------------------
    def color(self, file):
        img = skimage.data.imread(file)
        yuv = rgb2yuv(img)
        yuv[:,:,0] = self.effect
        self.color_image = yuv2rgb(yuv)
        scipy.misc.imsave("color_image.jpg", self.color_image)
#############################################################################
### We call function.
drawing = PencilDrawing()
drawing.draw("murje.jpg")
