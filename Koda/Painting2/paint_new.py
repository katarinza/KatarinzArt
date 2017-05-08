# Libraries:
import numpy
import scipy
from scipy import spatial
import skimage
from skimage import color, data, filter
import cairo
import pandas
# ----------
import sys
import random
import math
import colorsys

########################################################################
class PainterlyRendering():
    # ------------------------------------------------------------------
    def __init__(self, factor, brush_sizes, sigma, treshold, curvature, length_min, length_max, opacity, grid_size, h, s, v, r, g, b, jitter_max):
        """Create new painting with given parameters.
        Parametrs:
        brush_sizes ... set of brush sizes
        sigma ... blur factor
        treshold ... approximation treshold (painting vs source)
        curvature ... limit or exaggerate stroke curvature
        length_min ... minimum stroke length
        length_max ... maximum stroke length
        opacity ... paint opacity
        r, g, b, h, s, v ... factors to randomly add jitter to color components
        jitter_max ... maximum allowed jitter
        """
        self.factor = factor
        self.brush_sizes = brush_sizes
        self.sigma = sigma
        self.treshold = treshold
        self.curvature = curvature
        self.length_min = length_min
        self.length_max = length_max
        self.opacity = opacity
        self.grid_size = grid_size
        self.h, self.s, self.v = h, s, v
        self.r, self.g, self.b = r, g, b
        self.jitter_max = jitter_max
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------   
    def paint(self, file):
        """Main function.
        Parameters:
        file ... name of the path for image
        """
        ## Load image in rgb format.
        self.load_image(file)
        ## Surface for raw image.
        # RGBA format (32-bit)
        self.raw_data = numpy.zeros((self.height, self.width, 4), dtype = numpy.uint8)
        self.raw_canvas = cairo.ImageSurface.create_for_data(self.raw_data, cairo.FORMAT_ARGB32, self.width, self.height)
        self.data = numpy.zeros((self.height*self.factor, self.width*self.factor, 4), dtype = numpy.uint8)
        self.canvas = cairo.ImageSurface.create_for_data(self.data, cairo.FORMAT_ARGB32, self.width*self.factor, self.height*self.factor)
        self.context = cairo.Context(self.raw_canvas)
        self.fcontext = cairo.Context(self.canvas)
        ## TODO Compute the color we painted canvas initially.
        color = self.max_dist_color()
        # Paint the canvas.
        self.context.set_source_rgba(color[0], color[1], color[2])
        self.context.paint()
        self.fcontext.set_source_rgba(color[0], color[1], color[2])
        self.fcontext.paint()
        self.fcontext.paint()
        ## Loop over brush sizes.
        for r in self.brush_sizes:
            # Paint the surface.
            self.paintSurface(r)
            ime = "slika{0}.png".format(r)
            self.canvas.write_to_png(ime)
        self.raw_canvas.write_to_png("new_image.png")
        self.canvas.write_to_png("slika.png")
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    def load_image(self, file):
        try:
            self.source = skimage.data.imread(file) # ndarray
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
        duplicates = numpy.zeros((self.width*self.height, 3))
        for i in range(3):
            duplicates[:, i] = numpy.reshape(self.source[:,:,i], self.width*self.height)
        colors = pandas.DataFrame(duplicates).drop_duplicates().values
        voronoi_kdtree = scipy.spatial.cKDTree(colors)
        max_d = 0
        color = None
        for c in colors:
            dist, reg = voronoi_kdtree.query(c, k = 2, p = 2)
            if dist[1] > max_d:
                max_d = dist[1]
                color = c
        return (color[0], color[1], color[2], 255)
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    def paintSurface(self, r):
        ## Apply Gaussian blur.
        self.reference = skimage.filter.gaussian_filter(self.source, self.sigma*r)
        self.luminance = 0.3*self.reference[:,:,0] + 0.59*self.reference[:,:,1] + 0.11*self.reference[:,:,2]
        ## Gradient.
        self.sobel_x = scipy.ndimage.sobel(self.luminance, 0)  # horizontal derivatives
        self.sobel_y = scipy.ndimage.sobel(self.luminance, 1)  # vertical derivatives
        self.magnitude = numpy.hypot(self.sobel_x, self.sobel_y)
##        # We calculate normalized gradients.
##        self.grad_x = numpy.divide(self.sobel_x, self.magnitude)
##        self.grad_y = numpy.divide(self.sobel_y, self.magnitude)
        ## Pointwise difference image (surface_raw feat reference) which tells
        ## us where to repair our painting.
        difference = RGB_distance(self.raw_data[:,:,:3], 255*self.reference, True)
        ## Size of areas we will look up.
        grid = int(self.grid_size*r)
        ## List of strokes.
        # TODO Order of strokes !!!
        self.strokes = []
        ## Loop over grid.
        for x in range(0, self.width, grid):
            for y in range(0, self.height, grid):
                m1 = max(0, y - grid//2)
                m2 = min(self.height - 1, y + grid//2)
                n1 = max(0, x - grid//2)
                n2 = min(self.width - 1, x + grid//2)
                # Area and its error.
                area = difference[m1:m2+1,n1:n2+1]
                area_error = numpy.sum(area)/(grid**2)
                # If error is to big, we have to fix this area.
                if area_error > self.treshold:
                    # We find the largest error point.
                    (j, i) = scipy.ndimage.measurements.maximum_position(area)
                    (n0, m0) = (i + n1, j + m1)
                    # Call function which creates new stroke.
                    self.stroke(n0, m0, r)
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    def stroke(self, n0, m0, r):
        """Creates new stroke."""
        # For raw image we choose color at the position (n0, m0).
        color = self.reference[m0][n0]
        ## We compute control points.
        stroke = [] # control points for spline
        (n, m) = (n0, m0) # current point
        stroke.append((n, m))
        self.context.move_to(n, m) # raw image
        self.fcontext.move_to(n*self.factor, m*self.factor) # raw image
        (last_dx, last_dy) = (0, 0)
        # Find other control points.
        for i in range(self.length_max): # stroke can be only length_max long
            ## If stroke is already long enough, we check colors.
            if i > self.length_min:
                # Error: distance from reference color and current color on raw image.
                data_error = RGB_distance(256*self.reference[m][n][:3], self.raw_data[m][n][:3], False)
                # Error: distance from reference color and color of stroke.
                color_error = RGB_distance(256*self.reference[m][n][:3], 256*color, False)
                # TODO How to estimate error ?
                if data_error < color_error:
                    break
            ## Vanishing gradient.
            grad_error = 0 # TODO How big to take this grad_error ?
            if self.magnitude[m][n] <= grad_error:
                # TODO how to compute direction in this case.
                break
            else:
                ## We compute direction directly. 
                norm = math.sqrt(self.sobel_x[m][n]**2 + self.sobel_y[m][n]**2)
                gx, gy = self.sobel_x[m][n]/norm, self.sobel_y[m][n]/norm
                # Compute normal direction.
                dx, dy = -gx, gy
                # If necessary, reverse direction.
                if last_dx*dx + last_dy*dy < 0: (dx, dy) = (-dx, -dy)
                # Filter the stroke direction (depends on filter parameter).
                (dx, dy) = (self.curvature*dx + (1 - self.curvature)*last_dx, self.curvature*dy + (1 - self.curvature)*last_dy)
            last_dx, last_dy = dx, dy
            # TODO dx, dy has to be normalized ?
            if 0 <= m + r*dy < self.height and 0 <= n + r*dx < self.width:
                if self.clipping(n, m, n + r*dx, m + r*dy, r):
                    # Compute new point.
                    n, m = n + r*dx, m + r*dy
                else: break
            else: break
            ## Add new point.
            stroke.append((n, m))
            (cx, cy) = self.context.get_current_point()
            y1 = cy
            y2 = m
            x1 = x2 = (cx + n)/2
            self.context.curve_to(x1, y1, x2, y2, n, m)
            self.fcontext.curve_to(x1*self.factor, y1*self.factor, x2*self.factor, y2*self.factor, n*self.factor, m*self.factor)
        # Make stroke.
        self.context.set_line_width(r)
        self.context.set_source_rgba(color[0], color[1], color[2], 1)
        self.context.stroke()
        self.fcontext.set_line_width(r*self.factor)
        self.color = [color[0], color[1], color[2]]
        self.add_jitter_rgb()
        self.fcontext.set_source_rgba(self.color[0], self.color[1], self.color[2], self.opacity)
        self.fcontext.stroke()
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    def clipping(self, x1, y1, x2, y2, r):
        """
        x1, y1 ... start point
        x2, y2 ... endpoint
        Output:
        True ... point is legal
        False ... point is illegal
        """
        # We compute dx, dy.
        norm = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        dx, dy = (x2 - x1)/norm, (y2 - y1)/norm
        x, y = x1, y1
        lastSample = self.magnitude[y][x]
        while math.sqrt((x + dx)**2 + (y + dy)**2) <= r:
            (tempx, tempy) = (x + dx, y + dy)
            newSample = self.magnitude[y + dy][x + dx]
            if newSample < lastSample:
                return False
            x, y = x + dx, y + dy
            lastSample = newSample
        return True
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
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
########################################################################
## Distance functions in different color-spaces.      
def RGB_distance(M, N, bool):
    """Pointwise difference of two images represented by ndarrays M and N.
    """
    if not bool:
        return math.sqrt(sum((N - M)**2))
    d = numpy.power(numpy.subtract(N, M), 2)
    return numpy.sqrt(numpy.add(numpy.add(d[:,:,0], d[:,:,1]), d[:,:,2]))
# factor, brush_sizes, sigma, treshold, curvature, length_min, length_max, opacity, grid_size, h, s, v, r, g, b, jitter_max):
p = PainterlyRendering(8,[8,4,2],.5,150,0.8,4,16,0.6,1,0,1,0,0,1,0,0.2)
print 'paint'
p.paint("soncnice.jpg")
