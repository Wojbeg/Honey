import cv2
import mediapipe as mp
import numpy as np
import itertools
from math import dist

'''
Class will allow user to put mesh with 468 points on faces in pictures/ videos
Code, names of variables and process of initializing are based on official mediapipe 
documentation and example:
https://google.github.io/mediapipe/solutions/face_mesh.html

Class uses trained ML model to perform calculations and create mesh on face with 468 landmarks.
Thanks to that we are able to use them and add layers, images and other stuff like 
analysing posture, expression etc.
'''


class FaceMesh:
    """
    Names of variables are the same as in original documentation:
    static_image_mode - True if processing static image and False if video
    max_num_faces - Allow user to specify max number of detected faces
    min_detection_confidence - Minimum confidence of faces detection
    max_detection_confidence = Maximum confidence of faces detection
    drawing_spec_thickness - determines the thickness of the lines drawn on the faces
    drawing_circle_radius - determines the radius of the 468 points (dots) drawn on the faces
    refine_landmarks - If True allows for more accurate positioning of lips, eyes and eyebrows (requires more computing power),
    default False
    """

    def __init__(self, static_image_mode=False, max_num_faces=1, min_detection_confidence=0.5,
                 min_tracking_confidence=0.5, drawing_spec_thickness=1, drawing_circle_radius=1, drawing_circle_thickness=1,
                 refine_landmarks=False, connection_color=(0, 255, 0), points_color=(255, 0, 0)):
        self._static_image_mode = static_image_mode
        self._max_num_faces = max_num_faces
        self._min_detection_confidence = min_detection_confidence
        self._min_tracking_confidence = min_tracking_confidence
        self._refine_landmarks = refine_landmarks

        self._mp_drawing = mp.solutions.drawing_utils
        self._mp_drawing_styles = mp.solutions.drawing_styles
        self._mp_face_mesh = mp.solutions.face_mesh

        self._drawing_spec_mesh = self._mp_drawing.DrawingSpec(thickness=drawing_spec_thickness,
                                                               color=connection_color)

        self._drawing_spec_points = self._mp_drawing.DrawingSpec(circle_radius=drawing_circle_radius,
                                                                 thickness=drawing_circle_thickness,
                                                                 color=points_color)

        self.__face_mesh = self._mp_face_mesh.FaceMesh(static_image_mode=self._static_image_mode,
                                                       max_num_faces=self._max_num_faces,
                                                       min_detection_confidence=self._min_detection_confidence,
                                                       min_tracking_confidence=self._min_tracking_confidence,
                                                       refine_landmarks=self._refine_landmarks)


    #This function will generate face mesh
    def generateFaceMesh(self, image, drawing_mode=1, draw_mesh=True, draw_points=True):
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        #Here magic is happening - machine learning model trained by Mediapipe
        #return result and gives us landmarks
        self.__results = self.__face_mesh.process(image)
        image.flags.writeable = True

        faces = []

        img_height, img_width, img_channels = image.shape

        if self.__results.multi_face_landmarks:
            for face_landmarks in self.__results.multi_face_landmarks:

                if drawing_mode != 0:

                    points_style = None
                    if draw_points:
                        points_style = self._drawing_spec_points

                    mesh_style = None
                    if draw_mesh:
                        mesh_style = self._drawing_spec_mesh

                    connection_style = self._mp_face_mesh.FACEMESH_TESSELATION
                    if drawing_mode == 2:
                        connection_style = self._mp_face_mesh.FACEMESH_CONTOURS

                    self._mp_drawing.draw_landmarks(image, face_landmarks, connection_style, points_style, mesh_style)

                face = []

                for landmark_id, landmark in enumerate(face_landmarks.landmark):
                    #here we calculate actual position of landmark in image

                    landmark_x, landmark_y = int(landmark.x * img_width), int(landmark.y * img_height)
                    face.append([landmark_x, landmark_y])

                faces.append(face)

        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        return image, faces

    '''
    mediapipe contains useful indexes of body parts:
    
    mp_face_mesh.FACEMESH_FACE_OVAL - face line
    mp_face_mesh.FACEMESH_LIPS - lips
    mp_face_mesh.FACEMESH_LEFT_EYE - left eye
    mp_face_mesh.FACEMESH_RIGHT_EYE - right eye
    mp_face_mesh.FACEMESH_LEFT_EYEBROW - left eyebrow
    mp_face_mesh.FACEMESH_RIGHT_EYEBROW - right eyebrow
    
    Other can be defined due to their graphics with points
    
    '''

    def get_face_part_size(self, image, face_landmarks, face_part, draw=False, drawColor=(0,255,0), thickness=5):

        mesh_to_check = None

        #Yes, I could use as parameter their variables, or enum
        #but personally it was faster for me
        if face_part == 'LEFT_EYE':
            mesh_to_check = self._mp_face_mesh.FACEMESH_LEFT_EYE
        elif face_part == 'RIGHT_EYE':
            mesh_to_check = self._mp_face_mesh.FACEMESH_RIGHT_EYE
        elif face_part == 'MOUTH':
            mesh_to_check = self._mp_face_mesh.FACEMESH_LIPS
        elif face_part == 'FACE':
            mesh_to_check = self._mp_face_mesh.FACEMESH_FACE_OVAL
        elif face_part == 'LEFT_EYEBROW':
            mesh_to_check = self._mp_face_mesh.FACEMESH_LEFT_EYEBROW
        elif face_part == 'RIGHT_EYEBROW':
            mesh_to_check = self._mp_face_mesh.FACEMESH_RIGHT_EYEBROW
        else:
            return None

        face_part_landmarks_position = []
        list_of_landmarks_to_check = list(itertools.chain(*mesh_to_check))

        #here we obtain only landmarks from region of interest
        for landmark_index in list_of_landmarks_to_check:

            face_part_landmarks_position.append(face_landmarks[landmark_index])

        face_part_landmarks_position = np.array(face_part_landmarks_position)
        x, y, width, height = cv2.boundingRect(face_part_landmarks_position)

        if draw:
            image = cv2.rectangle(image, (x, y), (x + width, y + height), drawColor, thickness)

        return image, x, y, height, width, face_part_landmarks_position

    #x_shift and y_shift are used in normal coordinates (not computer ones)
    def overlay_body_part(self, image, overlay_image, face_landmarks, face_part, height_increase = 1.0, width_increase = 1.0, x_shift=0.0, y_shift=0.0):

        img_height, img_width, _ = image.shape

        #we have to make copy of our overlay image or it will become mess after iterations of transitions and masking out
        overlay_image_copy = overlay_image.copy()

        #we obtain height and width of body part
        _, part_x, part_y, part_height, part_width, _ = self.get_face_part_size(image, face_landmarks, face_part, draw=False)

        #here we calculate new size of overlay image
        new_height = int(part_height * height_increase)
        new_width = int(part_width * width_increase)

        #we are starting to calculate where is the region of interest
        start_x = int(part_x - (new_width - part_width)/2)
        start_y = int(part_y - (new_height - part_height)/2)

        #here we shift image, where user want e.g. above eyes
        start_x -= int(x_shift * part_width)
        start_y -= int(y_shift * part_height)

        overlay_height, overlay_width, _ = overlay_image_copy.shape

        new_overlay_height = int(overlay_width * new_height/overlay_height)

        resized_overlay_image = cv2.resize(overlay_image_copy, (new_width, new_overlay_height))

        new_overlay_height, new_overlay_width, _ = resized_overlay_image.shape

        #if image size is less than 0 something is wrong...
        if new_overlay_height < 0 or new_overlay_width < 0:
            return

        end_x = start_x + new_overlay_width
        end_y = start_y + new_overlay_height

        if start_x < 0:
            start_x = 0
        if start_y < 0:
            start_y = 0

        if end_x > img_width:
            end_x = img_width
        if end_y > img_height:
            end_y = img_height

        #here we obtain mask for overlaying image
        ret, mask = cv2.threshold(cv2.cvtColor(resized_overlay_image, cv2.COLOR_BGR2GRAY), 25, 255, cv2.THRESH_BINARY_INV+ cv2.THRESH_OTSU)

        #Out Region of Interest - part of face we want to cover with filter
        ROI = image[start_y:end_y, start_x:end_x]

        #we have to performe bitwise and operation to obtain new background and foreground using mask
        ROI_background = cv2.bitwise_and(ROI, ROI, mask)
        ROI_foreground = cv2.bitwise_and(resized_overlay_image, resized_overlay_image, mask)

        #sometimes person will be partially visible, so our mask will not cover whole image
        #this will cause to crash
        if ROI_background.shape[:2] != ROI_foreground.shape[:2]:
            return

        result_region = cv2.add(ROI_background, ROI_foreground)
        image[start_y:end_y, start_x:end_x] = result_region
        

    '''
    Function determine if mouth from landmarks is closed or open
    '''
    def is_mouth_open(self, face_landmarks, threshold=40):

        #13 and 14 are points on top and bottom lips
        mouth_size = dist(face_landmarks[13], face_landmarks[14])

        if mouth_size <= 0:
            mouth_size = 1

        #10 and 175 are point of whole face going throught mouth
        face_size = dist(face_landmarks[10], face_landmarks[175])

        if face_size <=0:
            face_size = -face_size

        return face_size / mouth_size < threshold

