import numpy
import scipy
from scipy import misc, integrate
import math

########################################################################
class Profil():
    """
    """

    def __init__(self, R, oblika="standard"):
        """
        R -- polmer voščenke (naravno število)
        oblika -- privzeta vrednost za obliko voščenke je "standard"
        """
        self.R = R
        self.oblika = oblika
        # ------------------
        self.size = 2*self.R + 1 # debelina voščenke
        self.set_profile() # nastavimo masko za profil (self.maska)
        self.min = numpy.min(self.profile) # višina najnižje točke
    # ------------------------------------------------------------------
    # Set wax mask.        
    # ------------------------------------------------------------------
    def set_profile(self):
        """
        Nastavimo začetne vrednosti profila.
        """
        indices = numpy.indices((self.size, self.size))
        r = numpy.sqrt((indices[0]-self.R)**2 + (indices[1]-self.R)**2)
        if self.shape == "sharp_conic":
            self.profile = 1 - self.h*(1 - r/(self.R+0.5))
            scipy.misc.toimage(numpy.where(self.profile <= 1, 0.1, 1), cmin=0.1, cmax=1).save("arean.png")
            self.profile = numpy.where(self.profile <= 1, self.profile - 0.2, 1)

            self.set_area() # sets area
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    def set_area(self):
        indices = numpy.indices((self.size+1, self.size+1))
        r = numpy.sqrt((2*indices[0]-self.size)**2 + (2*indices[1]-self.size)**2)
        out = numpy.where(r <= self.size, 0, 1)
        self.area = numpy.zeros((self.size, self.size))
        def line(i, j):
            s = sum([out[j][i], out[j][i+1], out[j+1][i+1], out[j+1][i]])
            f = lambda x: - math.sqrt(self.size**2 - x**2)
            if s == 4:
                self.area[j][i] = 1.
            elif s == 0:
                self.area[j][i] = 0.
            else:
                if s == 1:
                    x1 = 2*i - self.size
                    x2 = f(2*j - self.size)
                    int2 = 2*(x2-(2*(i+1)-self.size))
                elif s == 2:
                    if out[j][i+1] == 0:
                        x1 = f(2*(j+1) - self.size)
                        x2 = f(2*j - self.size)
                        int2 = 2*(x2-(2*(i+1)-self.size))
                    else:
                        x1 = 2*i - self.size
                        x2 = 2*(i+1) - self.size
                        int2 = 0
                elif s == 3:
                    x1 = f(2*(j+1) - self.size)
                    x2 = 2*(i+1) - self.size
                    int2 = 0
                int1 = scipy.integrate.dblquad(lambda x,y: 1., x1, x2, f, lambda y: 2*(j+1) - self.size)
                self.area[j][i] = 1 - (abs(int1[0]) + abs(int2))/4.
        for i in range(self.R):
            for j in range(self.R):
                line(i, j)
        int = scipy.integrate.dblquad(lambda y,x: 1., -1, 0,
                                      lambda x: -math.sqrt(self.size**2 - x**2), lambda x: 2 - self.size)
        self.area[self.R][0] = 1 - 2*int[0]/4.
        self.area[0][self.R] = 1 - 2*int[0]/4.
        for i in range(self.R+1):
            for j in range(self.R+1, self.size):
                self.area[j][i] = self.area[self.size-j-1][i]
        for i in range(self.R+1, self.size):
            for j in range(self.size):
                self.area[j][i] = self.area[j][self.size-i-1]
    # ------------------------------------------------------------------
    # Adjust height for wax mask.
    # ------------------------------------------------------------------
    def adjust_height(self, new_mask):
        self.height = new_mask
        self.min = numpy.min(self.height)
########################################################################

##wax = WaxMask(6, "sharp_conic", 0.8)
##scipy.misc.imsave("wax.png", wax.profile)
##scipy.misc.imsave("area.png", wax.area)
###scipy.misc.toimage(wax.area, cmin=0.1, cmax=0.7).save("area.png")
