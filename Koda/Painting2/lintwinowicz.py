# -*- coding: utf8 -*-
import numpy
import scipy
import skimage
from skimage import filter
from skimage import data
import cairo
import math
import sys
import colorsys
import random

########################################################################
class OneLayerPainting():
    
    def __init__(self, file, sigma, grid_size, brush_size_min, brush_size_max,
                 length_min, length_max, clip, theta, theta_p, color_p,
                 randomize):
        """Create new painting with given parametrs."""
        # Parameters for stroke generation. Centers of strokes, width,
        # length, clipping the edges, orientation of strokes, factor for
        # perturbation of theta, ...
        self.file = file # input image
        # TODO two different sigmas, one for edges and blurring, another for
        # gradient
        self.sigma = sigma # blur factor (how much we want to blur picture)
        self.grid = grid # controls the spacing of brush strokes
        self.brush_size_min = brush_size_min # minimum for brush size (radius)
        self.brush_size_max = brush_size_max # maximum for brush size (radius)
        self.length_min = length_min # minimum stroke length
        self.length_max = length_max # maximum stroke length
        self.clip = clip # if True, then strokes are clipped to the edges
        self.theta = theta # if theta is None, then orientations of strokes
                           # are computed from gradient of the image
        self.theta_p = theta_p # allowed perturbation for theta parameter
        # Rendering of strokes.
        # TODO How to choose color.
        # TODO using textures and lighting affects
        self.color_p = color_p # allowed perturbation for RGB color components
        self.randomize = randomize # strokes are drawn in randomized order
        
    # ---------------------------------------------------------------- #   
    def paint(self):
        """ Main function. """
        # We load image and save in ndarray self.source.
        self.load_image()
        # We create new surface for output image.
        self.data = numpy.zeros((self.height, self.width, 3))
        self.surface = cairo.ImageSurface.create_for_data(self.data, cairo.FORMAT_RGB24, self.width, self.height)
        # Create context with target surface.
        # TODO Here we create paper surface/texture.
        self.context = cairo.Context(self.surface)
        # Paint created surface.
        self.paintSurface()
        # Save the masterpiece :)
        self.surface.write_to_png("peter.png")
    # ------------------------------------------------------------------
    # We load image and save it as ndarray of image size.
    # ------------------------------------------------------------------
    def load_image(self):
        # Read file and save returned ndarray in self.source.
        try:
            self.source = skimage.data.imread(self.file)
            self.src = skimage.data.imread("segmentcolor.jpg")
        except:
            # TODO napaka, da file ne obstaja, odkomentiri to doma,
            # nato poglej kaj za eno napako da, če tega file, ki bi ga rad
            # naložil ni
            # nato ujemi to napako in preveri, če dela
            print "can't load " + self.file
            sys.exit()
        # Size of source ndarray.
        shape = self.source.shape
        self.height = shape[0]
        self.width = shape[1]
    # ------------------------------------------------------------------
        
    # ---------------------------------------------------------------- #
    def paintSurface(self):
        # Apply Gaussian blur.
        self.reference = skimage.filter.gaussian_filter(self.source, self.sigma, multichannel=True)
        self.ref = skimage.filter.gaussian_filter(self.src, self.sigma, multichannel=True)    
        self.luminance = 0.3*self.reference[:,:,0] + 0.59*self.reference[:,:,1] + 0.11*self.reference[:,:,2]
        self.sobel_x = scipy.ndimage.sobel(self.luminance, 0)  # horizontal derivative
        self.sobel_y = scipy.ndimage.sobel(self.luminance, 1)  # vertical derivative
        self.magnitude = numpy.hypot(self.sobel_x, self.sobel_y)
        # Create and f needed randomize the matrix with positions for
        # centers of strokes.
        indices = numpy.indices(self.magnitude.shape)
        centers = numpy.zeros((self.height//self.grid+1, self.width//self.grid+1, 2))
        for x in range(0, self.width, self.grid):
            for y in range(0, self.height, self.grid):
                centers[y//self.grid][x//self.grid][0] = indices[0][y][x]
                centers[y//self.grid][x//self.grid][1] = indices[1][y][x]
        if self.randomize:
            numpy.random.shuffle(centers)
        # We walk through centers. For each center we compute stroke and
        # paint it on surface. 
        for x in range(0, self.width//self.grid+1):
            for y in range(0, self.height//self.grid+1):
                (cy, cx) = centers[y][x]
                self.stroke(cx, cy)
                    
    # ---------------------------------------------------------------- #
    def stroke(self, cx, cy):
        """Creates new stroke and paint it on the surface."""
        # Set color for stroke.
        color = self.reference[cy][cx]
        if color_p:
            cr = random.randint(int(-self.color_p), int(self.color_p))/256.
            cg = random.randint(int(-self.color_p), int(self.color_p))/256.
            cb = random.randint(int(-self.color_p), int(self.color_p))/256.
            color[0] = color[0] + cr
            color[1] = color[1] + cg
            color[2] = color[2] + cb
        self.context.set_source_rgb(color[0], color[1], color[2])
        # Set stroke width.
        R = random.randint(int(self.brush_size_min*10),
                           int(self.brush_size_max*10))/10.
        self.context.set_line_width(R)
        self.context.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
        # Set stroke endpoints.
        self.set_endpoints(cx, cy)
        # set other stroke parametrs.
        self.context.set_line_cap(cairo.LINE_CAP_ROUND)
        # Paint stroke on surface.
        self.context.stroke()

    # ---------------------------------------------------------------- #
    def set_endpoints(self, cx, cy):
        if self.theta is None:
            # We have to compute the right orinetation for stroke.
            if self.magnitude[cy][cx] == 0:
                dx = math.cos(math.pi/4)
                dy = math.sin(math.pi/4)
            else:
                # get unit vector of gradient
                norm = math.sqrt(self.sobel_x[cy][cx]**2 + self.sobel_y[cy][cx]**2)
                (gx, gy) = (self.sobel_x[cy][cx]/norm, self.sobel_y[cy][cx]/norm)
                # compute a normal direction
                (dx, dy) = (-gx, gy)
            self.theta = math.atan(dy/dx)
        else:
            t = random.randint(int(-self.theta_p*1000), int(self.theta_p*1000))/1000.
            self.theta = self.theta + t
            dx = math.cos(self.theta)
            dy = math.sin(self.theta)
        l = random.randint(self.length_min, self.length_max)
        if self.clip:
            (x1, y1) = self.clipping(cx, cy, dx, dy, l)
            (x2, y2) = self.clipping(cx, cy, -dx, -dy, l)
        else:
            (x1, y1, x2, y2) = self.endpoints(cx, cy, dx, dy, l)
        self.context.move_to(x1, y1)
        self.context.line_to(x2, y2)

    # ---------------------------------------------------------------- #
    def clipping(self, cx, cy, dx, dy, length):
        (x, y) = (cx, cy)
        lastSample = self.magnitude[y][x]
        while True:
            (tempx, tempy) = (x + dx, y + dy)
            if distance((x, y), (tempx, tempy)) > length/2.:
                break
            if tempx >= self.width or tempy >= self.height:
                break
            newSample = self.magnitude[tempy][tempx]
            if newSample < lastSample:
                break
            (x, y) = (tempx, tempy)
            lastSample = newSample
        return (x, y)

    # ---------------------------------------------------------------- #
    def endpoints(self, cx, cy, dx, dy, length):
        x = length*math.cos(self.theta)
        y = length*math.sin(self.theta)
        (x1, y1) = (cx + x, cy + y)
        (x2, y2) = (cx - x, cy - y)
        return (x1, y1, x2, y2)

########################################################################
def distance((x1, y1), (x2, y2)):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

########################################################################
file = "monroe.jpg"
sigma = 2
grid = 6
brush_size_min = 8
brush_size_max = 12
length_min = 15
length_max = 30
clip = False
theta = math.pi/2.
theta_p = 0.1
color_p = 5
randomize = True

p=OneLayerPainting(file, sigma, grid, brush_size_min, brush_size_max,
                 length_min, length_max, clip, theta, theta_p, color_p,
                 randomize)
p.paint()
