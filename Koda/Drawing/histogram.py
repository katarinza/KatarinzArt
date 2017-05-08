import numpy
import math

def bright(sigma_b):
    s = []
    for i in range(256):
        s.append((1./sigma_b)*math.e**(-(1.-i)/sigma_b))
    sum_s = sum(s)
    s = [i/sum_s for i in s]
    return s

def mild(u_a, u_b):
    s = []
    for i in range(256):
        s.append(1./(u_b - u_a) if u_a <= i <= u_b else 0)
    sum_s = sum(s)
    s = [i/sum_s for i in s]
    return s

def dark(sigma_d, mu_d):
    s = []
    for i in range(256):
        s.append((1/math.sqrt(2*math.pi*sigma_d))*math.e**(-((i - mu_d)**2)/(2*sigma_d**2)))
    sum_s = sum(s)
    s = [i/sum_s for i in s]
    return s

def probability_hist(size, sigma_b = 9, u_b = 225, u_a = 105, w1 = 11, w2 = 37, w3 = 52, sigma_d = 11, mu_d = 90):
    v1 = numpy.array(bright(sigma_b))
    v2 = numpy.array(mild(u_a, u_b))
    v3 = numpy.array(dark(sigma_d, mu_d))
    p = (w1*v1 + w2*v2 + w3*v3)/100.
    p = size*p
    p = p.astype(int)
    s = skimage.data.imread('monroepred.png', as_grey=True)
    hist, bin_edges = numpy.histogram(s, bins = 257, range = (0,256), normed = True)
    return numpy.cumsum(p)

def histogram(src):
    hist, bin_edges = numpy.histogram(src, bins = 257, range = (0,256))
    return numpy.cumsum(hist)

def histogram_transform(src, w, h):
    """
    """
    src = src.astype(int)
    hist1 = histogram(src)
    hist2 = probability_hist(w*h)
    T = 256*[0]
    for i in range(1,256):
        for j in range(1,256):
            if hist1[i] >= hist2[j-1] and hist1[i] <= hist2[j]:
                T[i] = j
                break
    for i in range(h):
        for j in range(w):
            src[i][j] = T[src[i][j]]
    return src

##import skimage
##from skimage import data
##import scipy
##from scipy import misc
##
##moz = skimage.data.imread("stamos.jpg", as_grey=True)
##print moz
##s = numpy.shape(moz)
##w, h = s[1], s[0]
##slika = histogram_transform(moz*256, w, h)
##print slika
##scipy.misc.imsave("mozproba.jpg", slika)
