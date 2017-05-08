#!/usr/bin/env python
# -*- coding: cp1250 -*-

import numpy
from crayons_parameters import parameters_paper, colors
from skimage import data
import sys

# ===============
# Razred VOSCENKE
# ===============
class Voscenke():
    """
    """

    # -----------------------------------------------------------------#
    # Nastavitve za novo risbo z voščenkami.
    # -----------------------------------------------------------------#
    def __init__(self, mi_wax, mi_paper, wax_viscosity, alpha, beta,
                 wax_compression, force_accuracy, force, shape, R):
        """
        """
        self.mi_wax = mi_wax # frictional coefficient of wax
        self.mi_paper = mi_paper # frictional coefficient of paper
        self.wax_viscosity = wax_viscosity # viscosity of wax
        self.alpha = alpha # flow smear factor
        self.beta = beta # directional smear factor
        self.wax_compression = wax_compression # wax compression resistance factor
        self.force_accuracy = force_accuracy # force accuracy factor
        self.force = force
        self.shape = shape
        self.R = R
    # ------------------------------------------------------------------
    # Technical methods.
    # ------------------------------------------------------------------
    def load_image(self):
        # Read file and save returned ndarray in self.source.
        try:
            self.source = skimage.data.imread(self.file)
        except:
            #print "can't load " + self.file
            sys.exit()
        # Size of source ndarray.
        shape = self.source.shape
        self.height = shape[0]
        self.width = shape[1]
    # ------------------------------------------------------------------
    # Extracting curves from image.
    # ------------------------------------------------------------------
    def extract_curves(self):
        # Demo.
        self.curves = []
        points = []
        for i in range(10,20):
            points.append((i,i,[1,1]))
        self.curves.append((points, colors["red"]))
##        luminance = 0.3*self.source[:,:,0] + 0.59*self.source[:,:,1] + 0.11*self.source[:,:,2]
##        self.sobel_x = scipy.ndimage.sobel(luminance, 0)  # horizontal derivative
##        self.sobel_y = scipy.ndimage.sobel(luminance, 1)  # vertical derivative
##        self.magnitude = numpy.hypot(self.sobel_x, self.sobel_y)
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    def control_points(self, n0, m0):
        points = [] # list for control points
        color = self.source[m0,n0] # color for line
        (n, m) = (n0, m0) # current point
        (last_dx, last_dy) = (0, 0)# last direction
        # Find control points for Bezier curve.
        for i in range(self.length_max):
            if i > self.length_min:
                current_c = self.source[m,n]
                color_error = RGB_distance(256*current_c, 256*color)
                if color_error > self.color_eps:
                    break
            # Detect vanishing gradient.
            if self.magnitude[m,n] == 0:
                break
            # Get unit vector of gradient.
            norm = math.sqrt(self.sobel_x[m,n]**2 + self.sobel_y[m,n]**2)
            (gx, gy) = (self.sobel_x[m,n]/norm, self.sobel_y[m,n]/norm)
            # Compute a normal direction.
            (dx, dy) = (-gx, gy)
            # If necessary, reverse direction.
            if last_dx*dx + last_dy*dy < 0:
                (dx, dy) = (-dx, -dy)
            # New point.
            (m, n) = (m + self.R*dy, n + self.R*dx)
            if m >= self.height or n >= self.width:
                (m, n) = (m - self.R*dy, n - self.R*dx)
                break
            (last_dx, last_dy) = (dx, dy)
    # ------------------------------------------------------------------
    
    # ------------------------------------------------------------------
    def coloring(self):
        # Load image and save image's dimensions.
        self.load_image()
        # Extract curves from given image.
        self.extract_curves()
        # Crayon's height mask.
        self.wax_mask = wax_mask.WaxMask(self.shape, self.R)
        # Create dicitonary for layers.
        self.layer = Layer(self.width, self.height)
        # Set ndarray for paper texture.
        self.paper = PaperTexture(self.width, self.height)
        # Matrix with indices for smearing.
        self.matrix_smear = numpy.array([[[-1, 1], [0, 1], [1, 1]],
                                         [[-1, 0], [0, 0], [1, 0]],
                                         [[-1,-1], [0,-1], [1,-1]]])
        # In loop we will draw curves from self.curves.
        for curve in self.curves:
            for point in curve[0]:
                x, y = point[0], point[1]
                self.adjust_crayon_height(point)
                self.smear_existing_wax(point)
                self.add_new_wax(point, curve[1])
    # ------------------------------------------------------------------
    # Smear existing wax.
    # ------------------------------------------------------------------
    def smear_existing_wax(self, point):
        x, y = point[0][0], point[0][1]
        dx, dy = point[1][0], point[1][1]
        # Bounded height for paper and layers. (Mask is 3x3.)
        height_paper_bounded = self.paper.height[y-self.R-1:y+self.R+2,x-self.R-1:x+self.R+2]
        height_layer_bounded = self.layer.height[y-self.R-1:y+self.R+2,x-self.R-1:x+self.R+2]
        # For each cell in self.wax_mask ...
        for i in range(1, self.R*2+2):
            for j in range(1, self.R*2+2):
                # Firstly we set smearing matrix.
                def cos(v, m):
                    mm = numpy.zeros((3,3))
                    for x1 in range(3):
                        for y1 in range(3):
                            mm[y1,x1] = numpy.sum(numpy.multiply(self.matrix_smear[y1,x1],[dx, dy]))
                    return mm
                # Directional heading of the crayon.
                matrix_directional = cos(point_direction, self.matrix_smear)
                # Location heading of the crayon.
                matrix_height = (height_paper_bounded[j,i] + height_layer_bounded[j,i]) - (height_paper_bounded[j-1:j+2,i-1:i+2] + height_layer_bounded[j-1:j+2,i-1:i+2])
                matrix_height = numpy.where(matrix_height > 0, matrix_height, 0)
                smear_mask = numpy.add(self.alpha*matrix_directional, self.beta*matrix_height)
                smear_mask = (self.wax_viscosity/numpy.sum(smear_mask))*smear_mask
                # Amount of wax which will be distributed to its neighbors.
                # TODO probably it is multiplied by height_layer_bounded[j, i] 
                amount = height_layer_bounded[j, i]*(height_layer_bounded[j, i] + height_paper_bounded[j, i] - self.wax_mask[j-1, i-1])
                # Layers with removed wax from cell.
                # TODO Iz te toÄŤke niÄŤ ne odstranimo waxa na tem mestu,
                # Why, I don't know yet. Ampak je posebi en algoritem,
                # ki naredi toÄŤno to.
                indices = []
                h = 0
                delta_layers = self.layer.layers[(x-self.R-1+i,y-self.R-1+j)]
                l = len(delta_layers)
                while h < amount and l > 0:
                    indices.prepend(l)
                    h += delta_layers[l-1][0]
                    l -= 1
                # Distributing wax around.
                for n in range(-1, 2):
                    for m in range(-1, 2):
                        for k in indices:
                            self.layer.append_layer(y-self.R-1+j+m, x-self.R-1+i+n, smear_mask[m,n]*delta_layers[k][0], delta_layers[k][1])
    # ------------------------------------------------------------------
    # Adjust crayon height.
    # ------------------------------------------------------------------
    def adjust_crayon_height(self, point):
        """
        Parameters:
        point = ((x, y), (dx, dy))
        """
        x, y = point[0][0], point[0][1]
        # Heights of pixels on paper and complete height for wax layers.
        height_paper = self.paper.height_paper[y-self.R:y+self.R+1, x-self.R:x+self.R+1]
        height_layers = self.paper.height_layers[y-self.R:y+self.R+1, x-self.R:x+self.R+1]
        h_crayon = self.wax_mask.height # minimal distance from the gross plane of paper
        h_min = numpy.min(height_p)
        h_max = numpy.max(height_p)
        # Loop ... Newton's method
        while h_max - h_min > self.force_accuracy:
            h_mid = (h_max + h_min)/2.
            delta_h = height_paper + height_layers - (self.wax_mask.profile - h_crayon + h_mid)
            force_mid = numpy.sum(numpy.where(delta_h > 0, delta_h, 0)*self.wax_compression)
            if force < force_mid: h_min = h_mid
            else: h_max = h_mid
        # Adjust wax crayon's height.
        h_mid = (h_max + h_min)/2.
        self.wax_mask.adjust_height(h_mid)
    # ------------------------------------------------------------------
    # We add wax to the layers.
    # ------------------------------------------------------------------
    def add_new_wax(self, point, color):
        # point ... (coordinates = (x, y), direction = (dx, dy))
        x, y = point[0][0], point[0][1]
        dx, dy = point[1][0], point[1][1] # current direction of drawing
        dx, dy = dx/max(dx,dy), dy/max(dx,dy)
        # Heights.
        height_paper = self.paper.height_paper[y-self.R:y+self.R+1,x-self.R:x+self.R+1]
        height_direction = self.paper.height_paper[y-self.R+dy:y+self.R+dy+1,x-self.R+dx:x+self.R+1+dx]
        height_layer = self.paper.height_layers[y-self.R:y+self.R+1,x-self.R:x+self.R+1]
        # Slope and force vector.
        vector_s = numpy.zeros((self.R*2+1, self.R*2+1, 3))
        vector_s[:,:,0] = dx
        vector_s[:,:,1] = dy
        vector_s[:,:,2] = height_direction - height_paper
        vector_f = numpy.zeros((self.R*2+1, self.R*2+1, 3))
        vector_f[:,:,0] = dx
        vector_f[:,:,1] = dy
        vector_f[:,:,2] = -self.force
        # Coefficient.
        alpha = numpy.divide(1, numpy.add(1,self.wax_mask))
        mi = numpy.multiply(alpha, self.mi_paper) + numpy.multiply(1-alpha, self.mi_wax)
        # Functions.
        def absolute(m):
            new = numpy.zeros((self.R*2+1, self.R*2+1))
            for i in range(self.R*2+1):
                for j in range(self.R*2+1):
                    new[j,i] = numpy.sqrt(numpy.sum(m[j,i,:]**2))
            return new
        def sin(v1, v2):
            return numpy.divide(absolute(numpy.cross(v1, v2)), numpy.multiply(absolute(v1), absolute(v2)))
        # Amount of new wax.
        delta = mi*numpy.multiply(height_direction - self.wax_mask, sin(vector_s, vector_f))
        self.wax_mask.adjust_height(delta)
        self.paper.layers.append_layer(x, y, delta, color)
    # ------------------------------------------------------------------
    # Reclaim Wax.
    # ------------------------------------------------------------------
    def reclaim_wax(self, point):
        x, y = point[0][0], point[0][1]
        dx, dy = point[1][0], point[1][1]
        # Bounded height for paper and layers. (Mask is 3x3.)
        height_paper_bounded = self.paper.height[y-self.R-1:y+self.R+2,x-self.R-1:x+self.R+2]
        height_layer_bounded = self.layer.height[y-self.R-1:y+self.R+2,x-self.R-1:x+self.R+2]
        # For each cell in self.wax_mask ...
        for i in range(1, self.R*2+2):
            for j in range(1, self.R*2+2):
                def cos(v, m):
                    mm = numpy.zeros((3,3))
                    for x1 in range(3):
                        for y1 in range(3):
                            mm[y1,x1] = numpy.sum(numpy.multiply(self.matrix_smear[y1,x1,:],[dx, dy]))
                    return mm
                mask_s = cos(point_direction, self.matrix_smear)
                mask_s = numpy.where(mask_s > 0, mask_s, 0)
                mask_s = (self.force*self.wax_reclamation/numpy.sum(mask_s))*mask_s
                # Amount.
                # TODO
                amount = max(0, height_paper_bounded[j, i] - height_layer_bounded[j, i])
   
    # ------------------------------------------------------------------
    # Render the image.
    # ------------------------------------------------------------------
    def render(self):
        self.image = numpy.zeros((self.height, self.width, 3)) # resulting picture
        for i in range(self.width):
            for j in range(self.height):
                colour = self.paper.color[i, j]
                for l in self.paper.layers[(i, j)]:
                    colour_t = numpy.multiply((l[1][3]*l[1][:3])**l[0], colour)
                    colour_s = 1 - (1 - l[1][:3])**(l[1][4]*l[0])
                    self.image[j,i,:] = numpy.add(colour_t + colour_s)
########################################################################
        
########################################################################
class Layer():
    """
    Attributes:
    self.layers ... dictionary with point locations as keys and list of
                    tuples (height, color) as attributes
    self.height ... ndarray with total height
    """

    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.set_layers()
    # ------------------------------------------------------------------
    # We set colors and heights for paper - paper texture.
    # ------------------------------------------------------------------
    def set_layers(self):
        self.layers = {} # empty dictionary
        for i in range(self.w):
            for j in range(self.h):
                self.layers[(i, j)] = []
    # ------------------------------------------------------------------
    # Methods on class Layer.
    # ------------------------------------------------------------------
    def append_layer(self, i, j, height, color):
        self.height_paper[j,i] += height
        self.layers[(i, j)].append((height, color))        
########################################################################

def RGB_distance(c1, c2):
    return math.sqrt(sum((c1 - c2)**2))
