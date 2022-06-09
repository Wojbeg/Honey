import cv2
import numpy as np

'''
This contains basic operations on images
But in this version they are not used yet...
In 1.1 alpha there will be use for them.
'''

def rotate_image(image, angle, scale):
    #this will rotate image by angle and scale it

    height, width = image[:2]
    img_center = (width/2, height/2)
    matrix = cv2.getRotationMatrix2D(center=img_center, angle=angle, scale=scale)
    img_rotated = cv2.warpAffine(image, matrix, (width, height))
    return img_rotated

def shift_image(image, x=0, y=0):
    #this will shift image in specified directions

    height, width = image[:2]
    matrix = np.float32([[1, 0, x], [0, 1, y]])
    img_shifted = cv2.warpAffine(image, matrix, (width, height))
    return img_shifted
