import numpy
import scipy
from scipy import signal, misc
import skimage
from skimage import filter


mask_lunar = numpy.array([[0,0,0,0,1,1,1,1,1],
                          [0,0,0,0,1,1,1,1,1],
                          [0,0,0,0,1,1,1,1,1],
                          [0,0,0,1,1,1,1,1,0],
                          [1,1,1,1,1,1,1,1,0],
                          [1,1,1,1,1,1,1,0,0],
                          [1,1,1,1,1,1,0,0,0],
                          [1,1,1,1,1,0,0,0,0],
                          [1,1,1,0,0,0,0,0,0]])

mask_lunar = numpy.array([[0,0,0,0,0,0,0,1,1,1,1,1,1,1,1],
                          [0,0,0,0,0,0,0,1,1,1,1,1,1,1,1],
                          [0,0,0,0,0,0,0,1,1,1,1,1,1,1,1],
                          [0,0,0,0,0,0,0,1,1,1,1,1,1,1,1],
                          [0,0,0,0,0,0,0,1,1,1,1,1,1,1,1],
                          [0,0,0,0,0,0,0,1,1,1,1,1,1,1,0],
                          [0,0,0,0,0,0,1,1,1,1,1,1,1,1,0],
                          [0,0,0,0,0,1,1,1,1,1,1,1,1,1,0],
                          [1,1,1,1,1,1,1,1,1,1,1,1,1,0,0],
                          [1,1,1,1,1,1,1,1,1,1,1,1,1,0,0],
                          [1,1,1,1,1,1,1,1,1,1,1,1,1,0,0],
                          [1,1,1,1,1,1,1,1,1,1,1,1,1,0,0],
                          [1,1,1,1,1,1,1,1,1,1,1,1,1,0,0],
                          [1,1,1,1,1,1,1,1,0,0,0,0,0,0,0],
                          [1,1,1,1,1,0,0,0,0,0,0,0,0,0,0]])
##
mask_cross = numpy.array([[0,0,0,1,1,1,0,0,0],
                          [0,0,0,1,1,1,0,0,0],
                          [0,0,0,1,1,1,0,0,0],
                          [1,1,1,1,1,1,1,1,1],
                          [1,1,1,1,1,1,1,1,1],
                          [1,1,1,1,1,1,1,1,1],
                          [0,0,0,1,1,1,0,0,0],
                          [0,0,0,1,1,1,0,0,0],
                          [0,0,0,1,1,1,0,0,0]])
##
random = numpy.random.random((683, 1024))*0.2+0.8
masked = scipy.signal.convolve2d(random, mask_cross, 'same')
masked = masked + abs(masked.min())
masked = masked/(masked.max()*4)+0.4
scipy.misc.imsave("mask.png", masked)
masked = scipy.signal.convolve2d(random, mask_lunar, 'same')
masked = masked + abs(masked.min())
masked = masked/(masked.max()*4)+0.25
scipy.misc.imsave("mask1.png", masked)

array = numpy.zeros((683, 1024))
for i in range(1024):
    array[:,i] = (i%10)/10. 
for i in range(683):
    array[i,:] = array[i,:]*(i%5)/5.
array = array*0.2+0.8
scipy.misc.imsave("p1.png", array)
masked = scipy.signal.convolve2d(array, mask_lunar, 'same')
masked = masked + abs(masked.min())
masked = masked/(masked.max()*4)+0.25
scipy.misc.imsave("mask2.png", masked)


