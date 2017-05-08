import scipy
from scipy import optimize
import numpy
from math import log10

def optimize(H, J, lbd=0.2):
    shape = numpy.shape(H)
    w, h = shape[1], shape[0]
    x0 = numpy.zeros((1, w*h))
    args = (2*h*w)*[0]
    args[:w*h] = [item for sublist in H.tolist() for item in sublist]
    args[w*h:] = [item for sublist in J.tolist() for item in sublist]
    opt = scipy.optimize.fmin_cg(f, x0, args=tuple(args))
    return opt
    
def f(x, *args):
    H = args[:len(x)]
    J = args[len(x):]
    logH = [log10(i) for i in H]
    logJ = [log10(i) for i in J]
    xlogH = [i*j for i,j in zip(x, logH)]
    return sum([i-j for i,j in zip(xlogH, logJ)])

import skimage
from skimage import data
import scipy
from scipy import misc

moz = skimage.data.imread("risbicat.jpg", as_grey = True)
t = skimage.data.imread("list.png", as_grey = True)
s = numpy.shape(t)
w, h = s[1], s[0]
print h, w
# slika =  numpy.power(t*255, numpy.linalg.norm(numpy.divide(numpy.log(moz1+0.1), numpy.log(t*255)),'fro')) + 0.3
slika = numpy.where(moz<245,numpy.multiply(t, moz), moz)
scipy.misc.imsave("rezultat.jpg", slika)



