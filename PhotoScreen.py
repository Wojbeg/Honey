import cv2
import os
import time
from kivy.app import App
from kivy.metrics import dp
from kivymd.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.swiper import MDSwiper, MDSwiperItem
from kivy import platform

from Constants import CAMERA_FPS
from SpecialEffects import *
from SelfieSegmentation import SelfieSegmentation
from FaceMesh import FaceMesh
from kivymd.uix.button import MDIconButton
from kivy.graphics.texture import Texture
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from kivy.properties import Clock

from Strings import STRINGS_PL


class PhotoScreen(Screen):

    '''
    This class/screen allow user to take photo with special effects
    '''

    def __init__(self, **kwargs):
        '''
        Constructor that create screen class
        '''

        super(PhotoScreen, self).__init__(**kwargs)
        print("\nPhotoScreen.__init__():", id(self), "\n")

        self.language = App.get_running_app().return_language()

        self.layout = MDBoxLayout()
        self.layout.orientation = 'vertical'

        self.add_widget(self.layout)

        self.float = MDFloatLayout()

        self.layout.add_widget(self.float)

        self.image = Image()
        self.float.add_widget(self.image)
        # self.image.pos_hint = {'center_x': .5, 'center_y': 0.5}

        self.edit_photo = MDIconButton(
            icon='image-edit'
        )

        self.take_picture_btn = MDIconButton(
            icon='camera',
            pos_hint={'center_x': 0.5, 'y': 0}
        )

        self.take_picture_btn.bind(on_press=self.save_image)
        self.edit_photo.bind(on_press=self.navigate_to_photo_edit)

        self.float.add_widget(self.take_picture_btn)
        self.float.add_widget(self.edit_photo)

        self.edit_photo.pos_hint = {'top': 1}
        self.edit_photo.pos_hint = {'center_x': 0.05, 'y': 0}

        # self.layout.add_widget(self.float)

        self.special_effect = None

        self.img_frame = None

        self.event = None
        self.capture = None

        self.load_textures()

        self.create_bottom_swiper()

        self.create_layout()


    def navigate_to_photo_edit(self, *args):
        App.get_running_app().screen_manager.navigate_to_Choose_file()



    def create_bottom_swiper(self):
        '''
        This function create snapchat-like swiper with effects.
        It looks better on smartphone like width.
        '''

        self.swiper = MDSwiper(width_mult = 15, items_spacing=5)

        # self.swiper.size_hint_x = 0.1
        self.swiper.size_hint_y = 0.1

        self.swiper.pos_hint = {'center_x': 0.5, 'y': 0.1}

        self.swiper.on_swipe = self.on_swiper_swipe


        for effect_image in SpecialEffects:
            item = MDSwiperItem()
            # item.size_hint_x = 0.5

            # item.height = dp(30)
            # item.size_hint_max_x = dp(30)

            fitImage = Image()
            fitImage.source = effect_image.value[1]
            # fitImage.size_hint_max_x = 0.2
            fitImage.radius = [20, ]

            item.width = dp(30)
            item.add_widget(fitImage)
            self.swiper.add_widget(item)

        self.float.add_widget(self.swiper)


    def on_swiper_swipe(self, *args):
        '''On swipe we take id of item and apply its effect'''
        self.apply_special_effect(self.swiper.get_current_index()-1)

    def load_textures(self):
        '''Loading textures from files'''

        # SPACE FILTER
        self.helmet = cv2.imread('resources/images/Astronaut_Helmet.png')
        self.cosmos = cv2.imread('resources/images/space.jpg')

        # DEVIL HORNS
        self.horns = cv2.imread('resources/images/devil_horns.png')

        # DOG
        self.dog_ears = cv2.imread("resources/images/dog_ears.png")
        self.dog_nose = cv2.imread("resources/images/dog_nose.png")
        self.dog_tounge = cv2.imread("resources/images/dog_tounge.png")

        # EYES
        self.left_eye = cv2.imread("resources/images/funny_eye_left.png")
        self.right_eye = cv2.imread("resources/images/funny_eye_right.png")


    def create_layout(self):
        '''
        This function create face detection and start camera (camera loading is pretty slow in kivy apps,
        without it app load and work way faster). Face detection uses Mediapipe module.
        It is trained machine learing algorithm that allow to detect faces, hands, posture
        body parts and their positions. More information is in each module
        '''

        '''Note: I did not allowed user to specify minimum detection confidence etc. Because in snapchat/ instagram 
        apps user can't do this either. App has to be easy for user and most of them probably don't want to play with 
        such settings so i set them, hardcoded by test and try what works and looks acceptable in alpha version in my 
        opinion. '''
        self.num_of_detections = int(App.get_running_app().number_of_detections)
        self.face_mesh_detector = FaceMesh(max_num_faces=self.num_of_detections, min_detection_confidence=0.5,
                                       min_tracking_confidence=0.5, drawing_spec_thickness=1,
                                       drawing_circle_thickness=1, drawing_circle_radius=1)

        self.selfie_segmentator = SelfieSegmentation()


        self.start_camera()


    def start_camera(self):
        '''
        This function start camera and set clock to update it
        with specified resolution (hardcoded to modern standard,
        not too low, not to high)

        In mobile devices screen is rotated, so resolution
        size is rotated too. (Not tested yet on mobile, mobile tests
        will be performed with version 1.1 alpha).
        '''
        self.capture = cv2.VideoCapture(0)

        if platform != 'android' and platform != 'ios':
            self.capture.set(3, 1920)
            self.capture.set(4, 1080)
        else:
            self.capture.set(3, 1080)
            self.capture.set(4, 1920)

        '''FPS is hardcoded too. 30 fps is standard now for mobile and desktop, 60 fps 
        is too high yet, mediapipe operations are done on CPU not GPU, so due to architecture and
        complex operations done 30 times per second.
        On mobile (and PCs) it can be hard to achieve even 30 fps with special effects...'''
        self.capture.set(cv2.CAP_PROP_FPS, int(CAMERA_FPS))

        self.event = Clock.schedule_interval(self.update_camera, 1.0 / CAMERA_FPS)


    def stop_camera(self):
        '''Function stop camera if we swich screen to other.
            Camera should be turned off when we don't use it.
        '''

        if self.event is not None:
            self.event.cancel()

        if self.capture is not None:
            self.capture.release()


    def update_camera(self, *args):
        '''
        Function updates camera in specified frame rate.
        It can put some special effects like dog ears, nose on user face.
        Additionally it can support special pose effects - like dog tongue
        if lips are not together (mouth is open).
        '''

        success, img = self.capture.read()
        self.img_frame = img
        transformed = img

        showMesh = False
        if self.special_effect == SpecialEffects.MESH:
            showMesh = True

        transformed, faces = self.face_mesh_detector.generateFaceMesh(transformed, showMesh)

        for face in faces:

            # if self.special_effect is not None:
            if self.special_effect == SpecialEffects.SPACE:
                transformed = self.selfie_segmentator.removeBackground(transformed, self.cosmos, 0.6)
                self.face_mesh_detector.overlay_body_part(transformed, self.helmet, face, "FACE", height_increase=1.5,
                                                  width_increase=1.5, y_shift=0.3)

            elif self.special_effect == SpecialEffects.DEVIL:
                self.face_mesh_detector.overlay_body_part(transformed, self.horns, face, "FACE",
                                                          height_increase=1.5, width_increase=1.5, y_shift=0.25)

            elif self.special_effect == SpecialEffects.DOG:
                self.face_mesh_detector.overlay_body_part(transformed, self.dog_ears, face, "FACE", height_increase=1.0, width_increase=1.5, y_shift=0.7)
                self.face_mesh_detector.overlay_body_part(transformed, self.dog_nose, face, "FACE", height_increase=0.8, width_increase=1.0, y_shift=0.5)

                if self.face_mesh_detector.is_mouth_open(face):
                    self.face_mesh_detector.overlay_body_part(transformed, self.dog_tounge, face, "MOUTH", height_increase=3.5, width_increase=2, y_shift=-1.4)

            elif self.special_effect == SpecialEffects.EYES:
                self.face_mesh_detector.overlay_body_part(transformed, self.right_eye, face, "LEFT_EYE", height_increase=5.5, width_increase=2.5)
                self.face_mesh_detector.overlay_body_part(transformed, self.left_eye, face, "RIGHT_EYE", height_increase=5.5, width_increase=2.5)
            else:
                pass

        flipped = cv2.flip(transformed, -1)

        if flipped is not None:

            buffer = flipped.tobytes()

            texture = Texture.create(size=(transformed.shape[1], transformed.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')

            self.image.texture = texture

        self.img_frame = transformed


    def apply_special_effect(self, num=-1):
        '''This function switch selected effect when user swipe his effect card'''

        if num == -1:
            self.special_effect = SpecialEffects.NORMAL
        elif num == 0:
            self.special_effect = SpecialEffects.SPACE
        elif num == 1:
            self.special_effect = SpecialEffects.DEVIL
        elif num == 2:
            self.special_effect = SpecialEffects.DOG
        elif num == 3:
            self.special_effect = SpecialEffects.EYES
        elif num == 4:
            self.special_effect = SpecialEffects.MESH
        elif num == 5:
            self.special_effect = SpecialEffects.EYES_MESH
        elif num == 6:
            self.special_effect = SpecialEffects.FISH



    def save_image(self, *args):
        '''
        This function save image to specified by user or default path.
        Name convention is IMG_timestampYearMonthDay_HourMinuteSecond.
        Thanks to that user can take sa many photos as he like without
        fear that some names will repeat and override other one.
        Prints are not for user, they are used for debugging
        '''

        if (self.img_frame is not None) and (self.capture is not None):
            print("PhotoScreen {}: proceeding to take photo".format(id(self)))
            current_time = time.strftime("%Y%m%d_%H%M%S")
            file_name = "IMG_" + current_time.format(current_time) + ".png"

            path = App.get_running_app().default_path

            cv2.imwrite(os.path.join(path, file_name), self.img_frame)

            toast(self.language.get('photo') + file_name + self.language.get('saved_photo'))
            print("PhotoScreen {}: photo has been taken".format(id(self)))
