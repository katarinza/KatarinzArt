import numpy 
########################################################################
class PaperTexture():
    """
    Attributes:
    self.colors ... ndarray with pixel colors
    self.height ... ndarray with pixel heights
    """

    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.set_colors()
        self.set_height()
    # ------------------------------------------------------------------
    # We set color scheme for paper.
    # ------------------------------------------------------------------
    def set_colors(self):
        self.colors = numpy.zeros((self.h, self.w, 3))
    # ------------------------------------------------------------------
    # We set height texture for paper.
    # ------------------------------------------------------------------
    def set_height(self):
        self.height = numpy.zeros((self.h, self.w))
########################################################################
