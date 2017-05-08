import numpy
import skimage
from skimage import data

class Torn():

    def __init__(self, file):
        self.file = file # tearing file
        self.load_image() # load image

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

    def torn(self):
        

    
        
        
