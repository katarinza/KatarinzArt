import numpy
#
def rgb2hsi(rgb):
    """
    Parameters
    ----------
    rgb : ndarray
          RGB values (0 <= value <=1) of an image.
    Returns
    -------
    Ndarray hsi with HSI values.
    """
    (h, w) = rgb.shape
    hsi = numpy.zeros((h, w, 3))
    r = rgb[:,:,0]
    g = rbg[:,:,1]
    b = rgb[:,:,2]
    (r-g+r-b)
    return hsi
#
def hsi2rgb(hsi):
    return rgb
