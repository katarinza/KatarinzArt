# -*- coding: cp1250 -*-
import numpy
import scipy
from scipy import signal
from scipy import ndimage
import skimage
from skimage import filter
from skimage import data
import math

# Denosing http://www.ipol.im/pub/art/2011/bcm_nlm/

########################################################################
class PencilDrawing():

    def __init__(self):
        self.w1 = 11 # weight for dark regions
        self.w2 = 37 # weight for mild tone regions
        self.w3 = 52 # weight for bright regions
        self.sigma_b = 9
        self.u_a = 105
        self.u_b = 225
        self.ni_d = 90
        self.sigma_d = 11
        self.combine = False # Tone drawing and sketch.
        self.color = False # Color image.
        self.bright = 50 # Upper bound for dark tones.
        self.dark = 50 # Lower bound for bright tones.
        self.size = 10
    # ------------------------------------------------------------------
    def draw(self, file):
        # Read file and save returned ndarray in self.source.
        self.source_c = skimage.data.imread(file) # Color version of input. 
        #self.source_g = skimage.data.imread(file, as_grey = True) # Grey version of input.
        # Compute the luminance of an image.
        self.source_l = 0.3*self.source_c[:,:,0] + 0.59*self.source_c[:,:,1] + 0.11*self.source_c[:,:,2]
        # Dimensions:
        shape = self.source_l.shape
        self.height = shape[0]
        self.width = shape[1]
        # Drawing:
        self.sketch()
        if self.combine:
            self.tonal()
            self.combine()
        if self.color:
            self.coloring()
    # ------------------------------------------------------------------
    def sketch(self):
        self.gradient = numpy.gradient(self.source_l) # central differences
        (self.grad_x, self.grad_y) = self.gradient
        self.magnitude = numpy.hypot(self.grad_x, self.grad_y)
        # Kernels ...
        self.set_kernels()
        # Response maps ...
        self.set_response_maps()
        # Classification ...
        self.set_classification()
        # Lines
        self.set_lines()
        # Rendering ...
        self.s = 256 - self.s_lines
        m = numpy.max(self.s)
        self.s = (self.s/m)*256
        scipy.misc.imsave("liness.jpg", self.s)
    # ------------------------------------------------------------------
    def set_kernels(self):
        self.kernels = {}
        # Horizontal line.
        K1 = numpy.zeros((self.size, self.size))
        index_i, index_j = numpy.indices(K1.shape)
        K1[index_i == self.size//2] = 1
        self.kernels["K1"] = K1
        # Line 20°
        K2 = numpy.zeros((self.size, self.size))
        k = self.size - 1
        for i in range(self.size//4 + 1, self.size - self.size//4 - 1):
            K2[i, k-1 : k+1] = 1
            k = k - 2
        K2[self.size - self.size//4 - 1, 0] = 1
        K2[self.size//4, self.size - 1] = 1
        self.kernels["K2"] = K2
        # Line 45°
        K3 = numpy.zeros((self.size, self.size))
        K3[index_i == self.size - index_j - 1] = 1
        self.kernels["K3"] = K3
        # Line 70°
        K4 = numpy.zeros((self.size, self.size))
        k = self.size - 1
        for i in range(self.size//4 + 1, self.size - self.size//4 - 1):
            K4[k-1 : k+1, i] = 1
            k = k - 2
        K4[0, self.size - self.size//4 - 1] = 1
        K4[self.size - 1, self.size//4] = 1
        self.kernels["K4"] = K4
        # Vertical line.
        K5 = numpy.zeros((self.size, self.size))
        K5[index_j == self.size//2] = 1
        self.kernels["K5"] = K5
        # Line -20°
        K6 = numpy.zeros((self.size, self.size))
        k = 0
        for i in range(self.size//4 + 1, self.size - self.size//4 - 1):
            K6[i, k : k+2] = 1
            k = k + 2
        K6[self.size//4, 0] = 1
        K6[self.size - self.size//4 - 1, self.size - 1] = 1
        self.kernels["K6"] = K6
        # Line -45°
        K7 = numpy.zeros((self.size, self.size))
        K7[index_i == index_j] = 1
        self.kernels["K7"] = K7
        # Line -70°
        K8 = numpy.zeros((self.size, self.size))
        k = 0
        for i in range(self.size//4 + 1, self.size - self.size//4 - 1):
            K8[k : k+2, i] = 1
            k = k + 2
        K8[self.size - 1, self.size - self.size//4 - 1] = 1
        K8[0, self.size//4] = 1
        self.kernels["K8"] = K8
    # ------------------------------------------------------------------
    def set_response_maps(self):
        self.response_maps = {}
        i = 0
        for key, K in self.kernels.iteritems():
            G = scipy.signal.convolve2d(self.magnitude, K, 'same')
            self.response_maps[key] = G
            scipy.misc.imsave("class%d.jpg"%i, G)
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
            scipy.misc.imsave("skica%d.jpg"%i, C)
            i = i + 1
    # ------------------------------------------------------------------
    def set_lines(self):
        self.lines = {}
        i = 0
        self.s_lines = numpy.zeros((self.height, self.width))
        for key, C in self.classification.iteritems():
            S = scipy.signal.convolve2d(C, self.kernels[key], 'same')
            self.classification[key] = S
            scipy.misc.imsave("lines%d.jpg"%i, S)
            i = i + 1
            self.s_lines = self.s_lines + S
        scipy.misc.imsave("lines.jpg", self.s_lines)
    # ------------------------------------------------------------------
    def combine(self):
        tone = self.tonal_p
        line = self.s
        print line
        print tone
        self.effect = (tone + line)/2.
        scipy.misc.imsave("risbica.jpg", self.effect)

    def rgb2yuv(color):
        """Function rgb2yuv converts given color from RGB color space in the
    YUV color space."""
        if color.shape:pass
        y = 0.3*color[:,:,0] + 0.59*self.so[:,:,1] + 0.11*self.so[:,:,2]
        u = 0.492*(self.so[:,:,2] - y)
        v = 0.877*(self.so[:,:,0] - y)
        self.hsv = numpy.zeros((self.height, self.width, 3))
        self.hsv[:,:,0] = self.tonal_p
        self.hsv[:,:,1] = u
        self.hsv[:,:,2] = v
        scipy.misc.imsave("hsv.jpg", self.hsv)

    def yuv2rgb(self):
        """Function yuv2rgb converts given color from YUV color space in the
    RGB color space."""
        r = self.hsv[:,:,0] + (1/.877)*self.hsv[:,:,2]
        g = self.hsv[:,:,0] - .395*self.hsv[:,:,1] - .581*self.hsv[:,:,2]
        b = self.hsv[:,:,0] + (1/.492)*self.hsv[:,:,1]
        self.color = numpy.zeros((self.height, self.width, 3))
        self.color[:,:,0] = r
        self.color[:,:,1] = g
        self.color[:,:,2] = b
        scipy.misc.imsave("color.jpg", self.color)
        
    def tonal(self):
        self.tonal_source = self.source
        self.set_p_dark()
        self.set_p_mild()
        self.set_p_bright()
        self.tone()
##    self.p = (1/numpy.max(self.tonal_p))*256*self.p
##    self.p = scipy.signal.spline_filter(self.p)
        scipy.misc.imsave("tonal.jpg", self.tonal_p)

    def tone(self):
        self.tonal_p = (self.w3*self.p_d + self.w2*self.p_m + self.w1*self.p_b)

    def set_p_dark(self):
        self.p_d = (1/math.sqrt(2*math.pi*self.sigma_d))*numpy.exp(-(numpy.square(self.tonal_source-self.ni_d))/(2*self.sigma_d**2))

    def set_p_bright(self):
        self.p_b = numpy.where(self.tonal_source <= 1, (1./self.sigma_b)*numpy.exp(-(1. - self.tonal_source)/self.sigma_b), 0)

    def set_p_mild(self):
        self.p_m = numpy.where(self.u_a <= self.tonal_source, (self.tonal_source)/(self.u_b - self.u_a), 0)
        self.p_m = numpy.where(self.u_b >= self.p_m, self.p_m, 0)
        
#############################################################################
### We call function.
drawing = PencilDrawing()
drawing.draw("stamos.jpg")
