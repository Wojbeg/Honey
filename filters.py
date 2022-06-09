import cv2
import numpy as np
from scipy.interpolate import UnivariateSpline
"""
This class contains popular filters that mimic ones we can find in
instagram, snapchat, gimp or photoshop apps.

Some of them were described in the book "Opencv 4 With Python Blueprints"
"""


# filter use opencv2 to transform image to grayscale
def filter_to_gray(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


# filter use opencv2 to find borders of object in image
def filter_to_canny(img, lower_threshold=30, upper_threshold=150):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return cv2.Canny(img, lower_threshold, upper_threshold)

'''
This filter perform automatic color correction to photo
'''
def filter_gray_word_correction(img):
    #we have flip to b,g,r or read from 2,1,0 or convert cv2 to rgb
    #because our video is in b,g,r format (blue, green, red)

    if img is not None:
        b, g, r = img[..., 0], img[..., 1], img[..., 2]
        illuminant_factor = [np.average(r), np.average(g), np.average(b)]
        scale_factor = (illuminant_factor[0]+illuminant_factor[1]+illuminant_factor[2])

        r = r*scale_factor/illuminant_factor[0]
        g = g*scale_factor/illuminant_factor[1]
        b = b*scale_factor/illuminant_factor[2]

        new_image = np.dstack((b, g, r))
        new_image = cv2.normalize(new_image, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        return new_image

    return None

#this function returns sketch
def filter_to_pencil_sketch(img):
    img_gray = filter_to_gray(img)
    img_blurred = cv2.GaussianBlur(img_gray, (31, 31), 0, 0)
    sketch_gray = cv2.divide(img_gray, img_blurred, scale=256)

    return sketch_gray

#this function allow to change brightness
def brightness(img, beta=50):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    v = cv2.add(v, beta)
    v[v > 255] = 255
    v[v < 0] = 0
    final_hsv = cv2.merge((h, s, v))
    return cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)

#this function allow to change drakness of photo
def darkness(img, beta=50):
    return brightness(img, -beta)

#this function invert colours of image
def invert(img):
    return cv2.bitwise_not(img)

#this function transform image to sepia
def filter_sepia(img):

    #first we transform to float for better values
    img_sepia = np.array(img, dtype=np.float64)
    #next we have to multipy image by sepia matrix
    img_sepia = cv2.transform(img_sepia, np.matrix([[0.272, 0.534, 0.131],
                                    [0.349, 0.686, 0.168],
                                    [0.393, 0.769, 0.189]]))
    #next we normalize too big values to max - 255
    img_sepia[np.where(img_sepia > 255)] = 255
    #transform back to int
    img_sepia = np.array(img_sepia, dtype=np.uint8)
    return img_sepia

#this function transform image to cartoon like
def filter_cartoon(img):
    gray = filter_to_gray(img)
    gray = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, 9)

    colored = cv2.bilateralFilter(img, 9, 250, 250)

    ret, edgeImage = cv2.threshold(edges, 150, 255, cv2.THRESH_BINARY)


    cartoon = cv2.bitwise_and(colored, colored, mask=edgeImage)


    return cartoon

'''
  Value of each pixel is between 0 and 255 inclusive. If we want to to transform
  every single pixel it will need big amount of computation.
  We know that these values are repeating. We can prepare lookup table, so we precompute
  these values and use them for pixel.
'''
def LookupTable(x, y):
  spline = UnivariateSpline(x, y)
  return spline(range(256))

'''
This function apply summer effect on photo
'''
def summer_effect(img):
    increaseLookupTable = LookupTable([0, 64, 128, 256], [0, 80, 160, 256])
    decreaseLookupTable = LookupTable([0, 64, 128, 256], [0, 50, 100, 256])
    blue_channel, green_channel, red_channel  = cv2.split(img)
    #here we are using our increase and decrease lookup tables to
    #make image look more red and less blue (like summer scenery)
    red_channel = cv2.LUT(red_channel, increaseLookupTable).astype(np.uint8)
    blue_channel = cv2.LUT(blue_channel, decreaseLookupTable).astype(np.uint8)
    sum = cv2.merge((blue_channel, green_channel, red_channel))
    return sum

'''
This function apply winter effect on photo
'''
def winter_effect(img):
    increaseLookupTable = LookupTable([0, 64, 128, 256], [0, 80, 160, 256])
    decreaseLookupTable = LookupTable([0, 64, 128, 256], [0, 50, 100, 256])
    blue_channel, green_channel, red_channel = cv2.split(img)
    #here we are doing opposite compared to summer effect
    red_channel = cv2.LUT(red_channel, decreaseLookupTable).astype(np.uint8)
    blue_channel = cv2.LUT(blue_channel, increaseLookupTable).astype(np.uint8)
    sum = cv2.merge((blue_channel, green_channel, red_channel))
    return sum

'''
Gotham filter was used by instagram. It slightly enhanced blue color, by
increasing lower mid values of blue and decreasing upper mid tone blue.
Effect increased contrast of mid tone values of red.
'''
def gotham_filter(img):
    increaseMidtoneLookupTable = LookupTable([0, 25, 51, 76, 102, 128, 153, 178, 204, 229, 255], [0, 13, 25, 51, 76, 128, 178, 204, 229, 242, 255])
    increaseLowermidtoneLookupTable = LookupTable([0, 16, 32, 48, 64, 80, 96, 111, 128, 143, 159, 175, 191, 207, 223, 239, 255], [0, 18, 35, 64, 81, 99, 107, 112, 121, 143, 159, 175, 191, 207, 223, 239, 255])
    decreaseUppermidtone = LookupTable([0, 16, 32, 48, 64, 80, 96, 111, 128, 143, 159, 175, 191, 207, 223, 239, 255], [0, 16, 32, 48, 64, 80, 96, 111, 128, 140, 148, 160, 171, 187, 216, 236, 255])
    blue_channel, green_channel, red_channel = cv2.split(img)
    red_channel = cv2.LUT(red_channel, increaseMidtoneLookupTable).astype(np.uint8)
    blue_channel = cv2.LUT(blue_channel, increaseLowermidtoneLookupTable).astype(np.uint8)
    blue_channel = cv2.LUT(blue_channel, decreaseUppermidtone).astype(np.uint8)
    sum = cv2.merge((blue_channel, green_channel, red_channel))
    return sum
