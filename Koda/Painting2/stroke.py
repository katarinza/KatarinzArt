import numpy
import skimage.data
import scipy.misc
import scipy.interpolate

########################################################################
class Stroke():
    """
    Stroke with texture and lighting.
    """
    # ------------------------------------------------------------------
    def __init__(self, canvas, R, type, alpha, alpha_map, color_map, color, control_points = [], end_points = []):
        """
        Parameters:
        canvas ... canvas on which we are painting
        R ... radius of brush
        type ... "spline" or "line"
        alpha ... parameter for adjusting color of bristles
        alpha_map ... from brush mask
        color_map ... matrix with colors from reference image
        color ... pixel color at the anchor point
        control_points ... control points for spline
        end_points ... endpoints for line
        """
        self.canvas = canvas
        self.R = R
        if type == "spline":
            self.B_cubic_spline(control_points)
        elif type == "line":
            self.line(end_points)
        else:
            print "error"
            return
        self.render(alpha_map, color_map, alpha, color)
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    def B_cubic_spline(self, control_points):
        """
        control_points ... control points for cubic B-spline
        """
        m = len(control_points[0])
        # [[x - coordinates], [y - coordinates]]
        tck, u = scipy.interpolate.splprep(control_points, s=0, k=3)
        n = 50
        unew = numpy.linspace(0, 1, n)
        self.points = scipy.interpolate.splev(unew, tck)
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    def line(self, end_points):
        """
        end_points ... [(start_x, start_y), (end_x, end_y)]
        """
        start, end = end_points[0], end_points[1]
        m = 100
        unew = numpy.linspace(start[0], end[0], m)
        k = float(end[1]-start[1])/float(end[0]-start[0])
        n = end[1] - k*end[0]
        self.points = []
        for i in unew:
            self.points.append((i, k*i + n))
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    def render(self, alpha_map, color_map, alpha, color):
        """ Render stroke with brush. """
        brush = Brush(self.R, alpha_map, color_map, color, alpha)
        for i in range(len(self.points[0])):
            p = (self.points[0][i], self.points[1][i])
            canvas_p  = self.canvas[p[1]-R:p[1]+R+1, p[0]-R:p[0]+R+1,:]
            self.canvas[p[1]-R:p[1]+R+1, p[0]-R:p[0]+R+1,:] = brush.paint(canvas_p)
    # ------------------------------------------------------------------
    
    # ------------------------------------------------------------------
    def height(self, alpha_map):
        pass
    
########################################################################
class Brush():
    # ------------------------------------------------------------------
    def __init__(self, R, alpha_map, color_map, color, alpha):
        """
        R ... brush size (radius)
        alpha_map ... intensity values of bristles
        color_map ... associated array from reference image
        color ... color of anchor point
        alpha ... parameter used in adjusting brush
        """
        self.R = R
        self.size = 2*R + 1 # size of brush (2*R + 1)
        self.alpha_map = alpha_map
        # Set the brush.
        self.set_brush_color(alpha_map, color_map, color, alpha)
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    def set_brush_color(self, alpha_map, color_map, color, alpha):
        perturbation = numpy.random.randint(-5, 5, size=(self.size, self.size, 4))
        self.brush_color = numpy.ones((self.size, self.size, 3))*255
        self.brush_color = alpha*color_map + (1-alpha)*color + perturbation
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    def paint(self, canvas):
        for i in range(3):
            self.brush_color[:,:,i] = numpy.where(alpha_map > 0.1, self.brush_color[:,:,i], canvas[:,:,i])
        new = self.brush_color*2
##        new = numpy.ones((self.size, self.size, 3))*255
##        for i in range(3):
##            new[:,:,i] = numpy.add(numpy.multiply(self.alpha_map, self.brush_color[:,:,i]), numpy.multiply(1-self.alpha_map, canvas[:,:,i]))
        return new
########################################################################

print "zacel delat"
imagep = skimage.data.imread("stamos.jpg")
image = numpy.ones((imagep.shape[0],imagep.shape[1],4))*255
image[:,:,:3] = imagep
shape = image.shape
height = shape[0]
width = shape[1]
canvas = numpy.ones((height, width, 4))*255
R = 10
type = "spline"
alpha = 0.9
alpha_map = skimage.data.imread("brush.jpg", as_grey = True)
color_map = image[300-10:300+11,300-10:300+11]
color = image[300,300]
x = [31, 80, 120, 150, 200, 240]
y = [31, 60, 90, 150, 300, 350]
control_points = [x, y]
print "pricel delati stroke"
stroke = Stroke(canvas, R, type, alpha, alpha_map, color_map, color, control_points = control_points)
scipy.misc.imsave("stroke.png", stroke.canvas)
