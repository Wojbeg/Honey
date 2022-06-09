import cv2
import mediapipe as mp
import numpy as np

'''
Class will allow user to remove background from image
Code is based on official mediapipe documentation, some comments were copied and pasted here
https://google.github.io/mediapipe/solutions/selfie_segmentation.html
'''

class SelfieSegmentation():

    """
    Model - from official documentation:
    0 or 1. 0 to select a general-purpose model, and 1 to
    select a model more optimized for landscape images
    """
    def __init__(self, model=1):
        self._segmentation_model = model
        self._mp_drawing = mp.solutions.drawing_utils
        self._mp_selfie_segmentation = mp.solutions.selfie_segmentation
        self._selfie_segmentation = self._mp_selfie_segmentation.SelfieSegmentation(self._segmentation_model)


    def removeBackground(self, image, bg_image = (192, 192, 192), blure_threshold=0.1):
        #This function allow user to cut out background and leave only people

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        results = self._selfie_segmentation.process(image)
        image.flags.writeable = True

        # Draw selfie segmentation on the background image.
        # To improve segmentation around boundaries, consider applying a joint
        # bilateral filter to "results.segmentation_mask" with "image".
        condition = np.stack(
            (results.segmentation_mask,) * 3, axis=-1) > blure_threshold

        if isinstance(bg_image, tuple):
            background = np.zeros(image.shape, dtype=np.uint8)
            background[:] = bg_image
            output_image = np.where(condition, image, background)
        else:

            bg_image_copy = bg_image.copy()
            bg_image_copy = cv2.resize(bg_image_copy, (image.shape[1], image.shape[0]), interpolation = cv2.INTER_AREA)

            output_image = np.where(condition, image, bg_image_copy)

        output_image = cv2.cvtColor(output_image, cv2.COLOR_RGB2BGR)

        return output_image

