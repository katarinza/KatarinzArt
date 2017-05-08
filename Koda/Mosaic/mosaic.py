import numpy
import scipy
import cairo
import math
import sys
import random
from scipy import ndimage
from scipy.spatial import Voronoi, voronoi_plot_2d
import skimage
import skimage.data
from collections import Counter
from scipy import misc
########################################################################

class Mosaic():

    def __init__(self, file, n = None, size = 3, metric = 1, rotate = True, color = True, treshold = 100, scale = 2):
        self.load_image(file) # save image as ndarray (also set height and width)
        if n is None: # set number of tiles
            self.set_n()
        else:
            self.n = n
        self.size = size # Size of tiles.
        self.metric = metric # 1-metric: square; 2-metric: Voronoi cell
        self.rotate = rotate # are tiles rotated ?
        self.color = color # color for tile: if True then average,
                           # otherwise color of centroid
        self.treshold = treshold # error (while ...) TODO
        self.scale = scale # Determine the size of output mosaic.
    # ------------------------------------------------------------------
    def load_image(self, file):
        # Read file and save returned ndarray in self.source.
        try:
            self.source = skimage.data.imread(file)
        except:
            print "can't load " + file
            sys.exit()
        # Size of image.
        shape = self.source.shape
        self.height = shape[0]
        self.width = shape[1]
    # ------------------------------------------------------------------        
    def set_n(self):
        # TODO
        self.n = 1000
    # ------------------------------------------------------------------        
    def mosaic(self):
        # Set centroids. Randomly chosen (uniform distribution).
        self.set_centroids()
        # Reestimating of centroids.
        self.tiling()
        # We set context.
        self.set_context()
        # Cementing ...
        self.cement()
        # Save the masterpiece :)
        self.surface.write_to_png("mosaic.png")
    # ------------------------------------------------------------------
    def set_centroids(self):
        s = self.width*self.height
        sample = random.sample(range(1, s+1), self.n)
        self.centroids = [] # list of centroids
        for i in sample:
            m = i//self.width
            n = i%self.width
            self.centroids.append((n, m))
    # ------------------------------------------------------------------
    def tiling(self):
        # We set some useful staff ...
        self.indices = numpy.indices(self.source.shape[:2])        
        # We must reshape self.indices to have required shape for KDtree.
        self.reshape = numpy.zeros((self.width*self.height, 2))
        self.reshape[:,0] = numpy.reshape(self.indices[1,:], self.width*self.height)
        self.reshape[:,1] = numpy.reshape(self.indices[0,:], self.width*self.height)
        # Iterations ...
        for k in range(5):
            self.nearest_points()
            self.change_centroids()
    # ------------------------------------------------------------------
    def nearest_points(self):
        # We create KDtree for self.centroids.
        voronoi_kdtree = scipy.spatial.cKDTree(self.centroids)
        point_dist, point_regions = voronoi_kdtree.query(self.reshape, p = self.metric)
        self.regions = point_regions # pointers to centroids
    # ------------------------------------------------------------------
    def set_vector_field(self):
        self.luminance = 0.3*self.source[:,:,0] + 0.59*self.source[:,:,1] + 0.11*self.source[:,:,2]
        self.sobel_x = scipy.ndimage.sobel(self.luminance, 0)  # horizontal derivative
        self.sobel_y = scipy.ndimage.sobel(self.luminance, 1)  # vertical derivative
        self.vector_field = numpy.arctan2(self.sobel_y, self.sobel_x)
    # ------------------------------------------------------------------
    def set_rotation_matrix(self, c):
        rotation_matrix = numpy.array([[math.cos(self.orient[c[1],c[0]]),
                                        -math.sin(self.orient[c[1],c[0]])],
                                       [math.sin(self.orient[c[1],c[0]]),
                                        math.cos(self.orient[c[1],c[0]])]])
        return rotation_matrix
    # ------------------------------------------------------------------
    def change_centroids(self):
        sizes = Counter(self.regions)
        for c in range(len(self.centroids)):
            condition = (self.regions == c)
            y = numpy.sum(numpy.extract(condition, self.reshape[:,1]))/sizes[c]
            x = numpy.sum(numpy.extract(condition, self.reshape[:,0]))/sizes[c]
            self.centroids[c] = (x,y)

    def cement(self):
        regions_reshape = self.regions.reshape(self.height*2, self.width*2)
        region = numpy.zeros((self.height*2, self.width*2, 3))
        region[:,:,0] = regions_reshape
        region[:,:,1] = regions_reshape
        region[:,:,2] = regions_reshape
        self.output = numpy.zeros((self.height*2, self.width*2, 3))
        self.set_vector_field()
        self.vector_field = self.vector_field.reshape(self.width*self.height)
        for c in range(len(self.centroids)):
            tile = Tile(self.centroids[c], self.vector_field, "square",
                        self.context, self.source, region, c, self.output)
            self.output = tile.create_tile()
        scipy.misc.imsave('ciracara.jpg', self.output)
        
    # ------------------------------------------------------------------
    def set_context(self):
        # We create new surface for output image.
        data = numpy.zeros((self.height, self.width, 3))
        self.surface = cairo.ImageSurface.create_for_data(data, cairo.FORMAT_RGB24,
                                                          self.width, self.height)
        # Create context with target surface.
        self.context = cairo.Context(self.surface)
    # ------------------------------------------------------------------
########################################################################
class Tile():

    def __init__(self, position, direction, shape, context, source, regions, c, output):
        self.x, self.y = position[0]*2, position[1]*2
        self.direction = direction
        self.shape = shape
        self.context = context
        self.source = source
        self.regions = regions
        self.c = c
        self.output = output
        
    def create_tile(self):
        if self.shape == "square":
            color = self.source[self.y//2, self.x//2]
            self.context.set_source_rgb(color[0]/255., color[1]/255., color[2]/255.)
            self.rotate()
            self.context.move_to(self.x + self.point1[0], self.y + self.point1[1])
            self.context.line_to(self.x + self.point2[0], self.y + self.point2[1])
            self.context.line_to(self.x + self.point3[0], self.y + self.point3[1])
            self.context.line_to(self.x + self.point4[0], self.y + self.point4[1])
            self.context.close_path()
            self.context.fill()
            
        if self.shape =="voronoi":
            color = self.source[self.y, self.x]
            shape = self.source.shape
            width = shape[1]
            height = shape[0]
##            self.context.set_source_rgba(color[0], color[1], color[2])
##            ones = numpy.ones((height, width, 3))*256
##            mask = numpy.where(self.regions == [self.c, self.c, self.c], color, ones)
##            output = "c{0}.png".format(self.c)
##            scipy.misc.imsave(output, mask)
##            data = numpy.fromfile(output, dtype=np.int64)
##            mask_surface = cairo.ImageSurface.create_from_png(output)
##            self.context.mask_surface(mask_surface, 0.0, 0.0)
##            self.context.fill()
            self.output = numpy.where(self.regions == [self.c, self.c, self.c], color, self.output)
        return self.output

    def rotate(self):
        angle = self.direction[self.c]
        rotation_matrix = numpy.array([[math.cos(angle), -math.sin(angle)],
                                       [math.sin(angle), math.cos(angle)]])
        self.size = 6
        self.point1 = numpy.dot(rotation_matrix, [[-self.size],[self.size]])
        self.point2 = numpy.dot(rotation_matrix, [[self.size],[self.size]])
        self.point3 = numpy.dot(rotation_matrix, [[self.size],[-self.size]])
        self.point4 = numpy.dot(rotation_matrix, [[-self.size],[-self.size]])

########################################################################                
m = Mosaic("stamos.jpg", 2000, 1, True)
m.mosaic()
