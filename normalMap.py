import numpy
from numpy import linalg
import skimage
from skimage import data
import matplotlib
from matplotlib import colors
import scipy
from scipy import misc

class NormalMap():

    def __init__(self, heightMap, image, aLight, gama):
        self.heightMap = heightMap
        self.image = image
        self.aLight = aLight
        self.gama = gama
        
    def normalMap(self):
        (h, w) = self.heightMap.shape
        # We add boundaries around heightMap.
        boundMap = numpy.zeros((h + 2, w + 2, 3))
        boundMap[1:h+1,1:w+1,2] = self.heightMap
        boundMap[0,1:w+1,2] = self.heightMap[0,:]
        boundMap[h+1,1:w+1,2] = self.heightMap[h-1,:]
        boundMap[1:h+1,0,2] = self.heightMap[:,0]
        boundMap[1:h+1,w+1,2] = self.heightMap[:,w-1]
        boundMap[0,0,2] = self.heightMap[0,0]
        boundMap[0,w+1,2] = self.heightMap[0,w-1]
        boundMap[h+1,w+1,2] = self.heightMap[h-1,w-1]
        boundMap[h+1,0,2] = self.heightMap[h-1,0]
        # 
        v1 = boundMap[0:h,0:w,:] - boundMap[1:h+1,1:w+1,:]
        v2 = boundMap[0:h,2:w+2,:] - boundMap[1:h+1,1:w+1,:]
        v3 = boundMap[2:h+2,2:w+2,:] - boundMap[1:h+1,1:w+1,:]
        v4 = boundMap[2:h+2,0:w,:] - boundMap[1:h+1,1:w+1,:]
        # Normals:
        w1 = numpy.cross(v1, v2)
        w2 = numpy.cross(v2, v3)
        w3 = numpy.cross(v3, v4)
        w4 = numpy.cross(v4, v1)
        # Normal:
        ww = (w1 + w2 + w3 + w4)/4
        self.normalPlane = ww
    
    def bumpMapping(self):
        # Normal map.
        self.normalMap()
        norm = numpy.sqrt(numpy.sum(self.normalPlane, axis = 2)) #todo ne vem ali je prav ?
        value = numpy.true_divide(self.normalPlane[:,:,2], norm)
        # RGB to HSV
        hsv_image = matplotlib.colors.rgb_to_hsv(self.image)
        hsv_image[:,:,2] = value**self.gama + self.aLight
        return matplotlib.colors.hsv_to_rgb(hsv_image)
    
file1 = "vzorec1.png"
source1 = skimage.data.imread(file1)
file2 = "vzorec2.png"
source2 = skimage.data.imread(file2, as_grey = True)
print source2
aLight = 10
gama = 1
normMap = NormalMap(source2, source1, aLight, gama)
output = normMap.bumpMapping()
scipy.misc.imsave("paint.jpg", output)
