# -*- coding: cp1250 -*-
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
class PainterlyRendering():
    # ------------------------------------------------------------------
    def __init__(self, file, brush_sizes, sigma, treshold, curvature,
                 length_min, length_max, opacity, grid_size, h, s, v,
                 r, g, b, jitter_max):
        """Create new painting with given parametrs (defining painting style)."""
        self.brush_sizes = brush_sizes # list of brush sizes (largest to smallest)
        self.sigma = sigma # blur factor
        self.treshold = treshold # approximation treshold (painting vs source)
        self.curvature = curvature # limit or exaggerate stroke curvature
        self.length_min = length_min # minimum stroke length
        self.length_max = length_max # maximum stroke length
        self.opacity = opacity # paint opacity
        self.grid_size = grid_size # controls the spacing of brush strokes
        self.h = h # factor to randomly add jitter to hue color component
        self.s = s # factor to randomly add jitter to saturation color comp.
        self.v = v # factor to randomly add jitter to value color component
        self.r = r # factor to randomly add jitter to red color component
        self.g = g # factor to randomly add jitter to green color component
        self.b = b # factor to randomly add jitter to blue color component
        self.jitter_max = jitter_max
        self.paint(file)
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------   
    def paint(self, file):
        """Main function."""
        self.load_image(file)
        # We create new surface for output image. Initially the surface is
        # painted a color C.
        self.data = numpy.zeros((self.height, self.width, 4), dtype = numpy.uint8)
        self.canvas = cairo.ImageSurface.create_for_data(self.data, cairo.FORMAT_ARGB32, self.width, self.height)
        # Create context with target surface.
        self.context = cairo.Context(self.surface)
        # TODO Compute color C.
        self.max_dist_color()
        C = (1, 1, 1, 1)
        self.context.set_source_rgba(C[0], C[1], C[2], C[3])
        self.context.paint()
        
        # Loop over brush sizes.
        for r in self.brush_sizes:
            # Paint the surface.
            self.paintSurface(r)
        # Save the masterpiece :)
        self.surface.write_to_png("jabolka2.png")
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    def load_image(self, file):
        # Read file and save returned ndarray in self.source.
        try:
            self.source = skimage.data.imread(file)
        except:
            print "can't load " + file
            sys.exit()
        # Size of source ndarray.
        shape = self.source.shape
        self.height = shape[0]
        self.width = shape[1]
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    def max_dist_color(self):
        colors = numpy.zeros((self.width*self.height, 3))
        for i in range(3):
            colors[:,i] = numpy.reshape(self.source[:,:,i], self.width*self.height)
        voronoi_kdtree = scipy.spatial.cKDTree(colors)
        max_d = 0
        color = None
        for c in colors:
            dist, reg = voronoi_kdtree.query(c, p = 2)
            if dist > max_d:
                max_d = dist
                color = c
        return point
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    def paintSurface(self, r):
        # Apply Gaussian blur.
        self.reference = skimage.filter.gaussian_filter(self.source, self.sigma*r)
        self.luminance = 0.3*self.reference[:,:,0] + 0.59*self.reference[:,:,1] + 0.11*self.reference[:,:,2]
        self.sobel_x = scipy.ndimage.sobel(self.luminance, 0)  # horizontal derivative
        self.sobel_y = scipy.ndimage.sobel(self.luminance, 1)  # vertical derivative
        self.magnitude = numpy.hypot(self.sobel_x, self.sobel_y)
        # Pointwise difference image (surface feat reference).
        difference = RGB_distance(self.data[:,:,:3], 255*self.reference, True)
##        self.paths = []
        # Forloop over difference array.
        grid = int(self.grid_size*r)
        # Randomized matrix of indices.
        indices = numpy.indices(difference.shape)
        random = numpy.zeros((self.height//grid+1, self.width//grid+1, 2))
        for x in range(0, self.width, grid):
            for y in range(0, self.height, grid):
                random[y//grid][x//grid][0] = indices[0][y][x]
                random[y//grid][x//grid][1] = indices[1][y][x]
        numpy.random.shuffle(random)
        for x in range(0, self.width//grid+1):
            for y in range(0, self.height//grid+1):
                # Area.
                (m, n) = random[y][x]
                m1 = max(0, m - grid//2)
                m2 = min(self.height - 1, m + grid//2)
                n1 = max(0, n - grid//2)
                n2 = min(self.width - 1, n + grid//2)
                area = difference[m1:m2+1,n1:n2+1]
                # Area error.
                area_error = numpy.sum(area)/(grid**2)
                # If error is to big, we have to fix this area.
                if area_error > self.treshold:
                    # We find the largest error point.
                    (j, i) = scipy.ndimage.measurements.maximum_position(area)
                    (m0, n0) = (j + m1, i + n1)
                    # Call function which creates new stroke.
                    self.stroke(m0, n0, r)
##        for p in self.paths:
##            self.context.append_path(p[0])
##            self.context.set_source_rgba(p[1][0],p[1][1],p[1][2])
##            self.context.set_line_width(r)
##            self.context.stroke()
                    
    # ---------------------------------------------------------------- #
    def stroke(self, m0, n0, r):
        """Creates new stroke."""
        # Color of stroke is the color of pixel (x, y).
        color = self.reference[m0][n0]
        # Current and last control point.
        (m, n) = (m0, n0)
        self.context.move_to(n, m)
        (last_dx, last_dy) = (0, 0)
        # Find control points for Bezier curve.
        for i in range(self.length_max):
            if i > self.length_min:
                ref = self.reference[m][n]
                data_error = RGB_distance(256*ref, self.data[m][n][:3], False)
                color_error = RGB_distance(256*ref, 256*color, False)
                if data_error < color_error:
                    break
            # detect vanishing gradient
            if self.magnitude[m][n] == 0:
                break
            # get unit vector of gradient
            norm = math.sqrt(self.sobel_x[m][n]**2 + self.sobel_y[m][n]**2)
            (gx, gy) = (self.sobel_x[m][n]/norm, self.sobel_y[m][n]/norm)
            # compute a normal direction
            (dx, dy) = (-gx, gy)
            # if necessary, reverse direction
            if last_dx*dx + last_dy*dy < 0:
                (dx, dy) = (-dx, -dy)
            # filter the stroke direction
            (dx, dy) = (self.curvature*dx + (1 - self.curvature)*last_dx,
                        self.curvature*dy + (1 - self.curvature)*last_dy)
            (dx, dy) = (dx/math.sqrt(dx**2 + dy**2), dy/math.sqrt(dx**2 + dy**2))
            (m, n) = (m + r*dy, n + r*dx)
            if m >= self.height or n >= self.width:
                (m, n) = (m - r*dy, n - r*dx)
                break
            (cx, cy) = self.context.get_current_point()
            y1 = cy
            y2 = m
            x1 = x2 = (cx + n)/2
            self.context.curve_to(x1, y1, x2, y2, n, m)
            (last_dx, last_dy) = (dx, dy)
        # Color of stroke is the color of pixel (x, y).
        color_start = self.reference[m0][n0]
        self.color = self.reference[m0][n0]
        color_stop = self.reference[m][n]
        pattern = cairo.LinearGradient(m0, n0, m, n)
        pattern.add_color_stop_rgba(0.3, color_start[0], color_start[1],
                                    color_start[2], self.opacity)
        pattern.add_color_stop_rgba(0.7, color_stop[0], color_stop[1],
                                    color_stop[2], self.opacity)
        self.context.set_source_rgba(self.color[0], self.color[1],
                                     self.color[2], self.opacity)
        self.context.set_line_width(r)
        self.context.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
        self.context.set_line_join(cairo.LINE_JOIN_BEVEL)
        self.add_jitter_rgb()
        self.add_jitter_hsv()
#        path = self.context.copy_path()
#        self.paths.append([path, color])
        self.context.stroke()
#        self.context.new_path()

    def clipping(self, t1, t2, R):
        """
        t1 ... start point
        t2 ... endpoint
        R ... brush radius
        Output:
        True ... point is legal
        False ... point is illegal
        """
        return True
        x, y = t1[0], t1[1]
        lastSample = self.magnitude[y][x]
        while True:
            (tempx, tempy) = (x + dx, y + dy)
            if distance((x, y), (tempx, tempy)) > R:
                return False
            newSample = self.magnitude[tempy][tempx]
            if newSample < lastSample:
                break
            (x, y) = (tempx, tempy)
            lastSample = newSample
        return True

    def add_jitter_rgb(self):
        self.add_jitter([self.r, self.g, self.b])

    def add_jitter_hsv(self):
        self.color = list(colorsys.rgb_to_hsv(self.color[0],self.color[1],self.color[2]))
        self.add_jitter([self.h, self.s, self.v])
        self.color = list(colorsys.hsv_to_rgb(self.color[0],self.color[1],self.color[2]))

    def add_jitter(self, jitter_p):
        """Adds jitter to the color."""
        for i in range(len(jitter_p)):
            jitter = random.randint(-int(self.jitter_max*100),
                                    int(self.jitter_max*100))/100.0
            p = random.randint(0, 100)/100.0
            if p <= jitter_p[i]:
                jitter_color = self.color[i] + jitter
                if jitter_color > 1: jitter_color = 1
                if jitter_color < 0: jitter_color = 0
                self.color[i] = jitter_color
            i = i + 1
             
### Distance functions in different color-spaces.      
def RGB_distance(M, N, bool):
    """Pointwise difference of two images represented by
       ndarrays M and N.
    """
    if not bool:
        return math.sqrt(sum((N - M)**2))
    d = numpy.power(numpy.subtract(N, M), 2)
    return numpy.sqrt(numpy.add(numpy.add(d[:,:,0], d[:,:,1]), d[:,:,2]))

p = PainterlyRendering("fakulteta.jpg",[8,4,2],.5,100,1,4,16,
1,1,0,1,0,0,1,0,0.1)
