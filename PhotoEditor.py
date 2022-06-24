import os
import cv2
from kivy.app import App
from kivy.metrics import dp
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivymd.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout
from kivy import platform
from kivymd.uix.label import MDLabel
from kivymd.uix.slider import MDSlider
from kivymd.uix.toolbar import MDToolbar
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.core.window import Window
import time

import filters
from Constants import BRIGHTNESS_MIN, BRIGHTNESS_MAX, BRIGHTNESS_VAL_INIT, DARKNESS_MIN, DARKNESS_MAX, \
    DARKNESS_VAL_INIT, CANNY_MIN, CANNY_MAX, CANNY_VAL_INIT, CANNY_MAX_MIN, CANNY_MAX_MAX, CANNY_MAX_VAL_INIT
from FiltersEnum import Filters
from Strings import STRINGS_PL


class PhotoEditor(Screen):

    def __init__(self, **kwargs):
        super(PhotoEditor, self).__init__(**kwargs)
        print("\nChooseFile.__init__():", id(self), "\n")

        #As i said in other class for now I will stick with
        #only Polish version but it can easily be extended to other versions
        self.__language = App.get_running_app().return_language()

        self.__image_tmp = None

        self.__path = None

        #this will hold current actions to apply
        self.__actions = []

        #this will hold information about changes
        #and allow to rollback them
        self.__back_images = []
        self.__current_changes = 0

        #crating main layout
        self.__layout = MDBoxLayout()
        self.__layout_in = MDBoxLayout()
        self.__layout.orientation = 'vertical'

        #in this case we use different orientation fr different platforms
        if platform != 'android' and platform != 'ios':
            self.__layout_in.orientation = 'horizontal'
        else:
            self.__layout_in.orientation = 'vertical'

        self.add_widget(self.__layout)

        #creating toolbar
        self.__toolbar = MDToolbar()
        self.__toolbar.title = self.__language.get('edit_photo')
        self.__toolbar.left_action_items = [['arrow-left-thick', lambda x: self.navigate_back(x)]]
        self.__toolbar.right_action_items = [['content-save', lambda x: self.save_image(x)]]
        self.__toolbar.elevation = 10

        self.__layout.add_widget(self.__toolbar)
        self.__layout.add_widget(self.__layout_in)

        #add photo frame
        self._image = Image()
        self.__layout_in.add_widget(self._image)

        #add scroll view for all effects panels
        self.__scroll = ScrollView()
        self.__scroll.size_hint = (1, 1)

        #grid for effects panels
        self.__grid = GridLayout()
        self.__grid.size_hint_y = 2
        self.__grid.cols = 1


        #calling a function to create panels for editing and set them up
        self.create_editing_settings()

        self.__scroll.add_widget(self.__grid)

        #enable scroll
        self.__scroll.do_scroll_y = True

        #label for informing user
        self.__edit_info = MDToolbar(anchor_title="center")
        self.__edit_info.title = self.__language.get('edit_photo_with_effects')
        self.__edit_info.size_hint_y = 0.1
        self.__edit_info.elevation = 10
        self.__edit_info.left_action_items = [['step-backward', lambda x: self.undo_changes(x)], ['check', lambda x: self.save_changes(x)]]


        self.__edit_info.text_color = self.__toolbar.specific_text_color
        self.__edit_info.halign = 'center'

        #layout for right box in editing pad
        self.__right_edit_label_box = MDBoxLayout()
        self.__right_edit_label_box.orientation = 'vertical'

        self.__right_edit_label_box.add_widget(self.__edit_info)
        self.__right_edit_label_box.add_widget(self.__scroll)

        self.__layout_in.add_widget(self.__right_edit_label_box)




    def create_editing_settings(self):
        #function add labels with effects to switch
        boxes = []
        box_height = dp(550)

        #list from enum
        boxes_names = [filter.value for filter in Filters]

        #creating layouts for each image filter
        for name in boxes_names:
            box = MDBoxLayout()
            box.height = box_height
            box.orientation = 'horizontal'

            label = MDLabel(text=name)
            label.padding_x = dp(5)
            label.size_hint_x = 0.3

            box.add_widget(label)

            boxes.append(box)
            self.__grid.add_widget(box)

        #creating layouts for selecting each image filter

        #gray
        #We create checkbox to apply effect
        self.__gray_check = CheckBox()
        #then we bind function to use aven checkbox change it state
        self.__gray_check.bind(active=self.apply_gray)
        boxes[0].add_widget(self.__gray_check)

        #sepia
        self.__sepia_check = CheckBox()
        self.__sepia_check.bind(active=self.apply_sepia)
        boxes[1].add_widget(self.__sepia_check)


        #invert
        self.__invert_check = CheckBox()
        self.__invert_check.bind(active=self.apply_invert)
        boxes[2].add_widget(self.__invert_check)

        #brightness
        self.__brightness_check = CheckBox()
        self.__brightness_check.bind(active=self.apply_brightness)

        self.__brightness_slider = MDSlider()
        self.__brightness_slider.bind(value=self.activated_slider)
        self.__brightness_slider.disabled = True
        self.__brightness_slider.min = BRIGHTNESS_MIN
        self.__brightness_slider.max = BRIGHTNESS_MAX
        self.__brightness_slider.value = BRIGHTNESS_VAL_INIT


        #There was no need to add it to self,
        #it is only used once internally and won't be acessed
        mini_brightness = MDBoxLayout()
        mini_brightness.orientation = 'vertical'
        mini_brightness.add_widget(self.__brightness_check)
        mini_brightness.add_widget(self.__brightness_slider)
        boxes[3].add_widget(mini_brightness)


        #darkness
        self.__darkness_check = CheckBox()
        self.__darkness_check.bind(active=self.apply_darkness)



        self.__darkness_slider = MDSlider()
        self.__darkness_slider.disabled = True
        self.__darkness_slider.bind(value=self.activated_slider)
        self.__darkness_slider.min = DARKNESS_MIN
        self.__darkness_slider.max = DARKNESS_MAX
        self.__darkness_slider.value = DARKNESS_VAL_INIT

        #Same here, won't be acessed and used so no self
        mini_darkness = MDBoxLayout()
        mini_darkness.orientation = 'vertical'
        mini_darkness.add_widget(self.__darkness_check)
        mini_darkness.add_widget(self.__darkness_slider)

        boxes[4].add_widget(mini_darkness)

        box_for_canny = MDBoxLayout()
        box_for_canny.orientation = 'vertical'


        self.__canny_check = CheckBox()
        self.__canny_check.bind(active=self.apply_canny)
        box_for_canny.add_widget(self.__canny_check)


        self.__canny_min = MDSlider()
        self.__canny_min.disabled = True
        self.__canny_min.bind(value=self.activated_slider)
        self.__canny_min.min = CANNY_MIN
        self.__canny_min.max = CANNY_MAX
        self.__canny_min.value = CANNY_VAL_INIT

        mini_canny_box = MDBoxLayout()
        mini_canny_box.orientation = 'horizontal'
        mini_canny_box.add_widget(MDLabel(text=self.__language.get('min')))
        mini_canny_box.add_widget(self.__canny_min)

        self.__canny_max = MDSlider()
        self.__canny_max.disabled = True
        self.__canny_max.bind(value=self.activated_slider)
        self.__canny_max.min = CANNY_MAX_MIN
        self.__canny_max.max = CANNY_MAX_MAX
        self.__canny_max.value = CANNY_MAX_VAL_INIT

        maxi_canny_box = MDBoxLayout()
        maxi_canny_box.orientation = 'horizontal'
        maxi_canny_box.add_widget(MDLabel(text=self.__language.get('max')))
        maxi_canny_box.add_widget(self.__canny_max)


        box_for_canny.add_widget(mini_canny_box)
        box_for_canny.add_widget(maxi_canny_box)

        boxes[5].add_widget(box_for_canny)



        self.__correction_check = CheckBox()
        self.__correction_check.bind(active=self.apply_correction)
        boxes[6].add_widget(self.__correction_check)

        self.__pencil_check = CheckBox()
        self.__pencil_check.bind(active=self.apply_pencil)
        boxes[7].add_widget(self.__pencil_check)

        self.__cartoon_check = CheckBox()
        self.__cartoon_check.bind(active=self.apply_cartoon)
        boxes[8].add_widget(self.__cartoon_check)

        self.__summer_check = CheckBox()
        self.__summer_check.bind(active=self.apply_summer)
        boxes[9].add_widget(self.__summer_check)

        self.__winter_check = CheckBox()
        self.__winter_check.bind(active=self.apply_winter)
        boxes[10].add_widget(self.__winter_check)

        self.__gotham_check = CheckBox()
        self.__gotham_check.bind(active=self.apply_gotham)
        boxes[11].add_widget(self.__gotham_check)


    def reset_actions(self):
        '''This function resets all actions'''
        self.__actions.clear()
        self.__brightness_slider.value = BRIGHTNESS_VAL_INIT
        self.__canny_min.value = CANNY_VAL_INIT
        self.__canny_max.value = CANNY_MAX_VAL_INIT

        self.__gray_check.state = 'normal'
        self.__sepia_check.state = 'normal'
        self.__invert_check.state = 'normal'
        self.__brightness_check.state = 'normal'
        self.__darkness_check.state = 'normal'
        self.__canny_check.state = 'normal'
        self.__correction_check.state = 'normal'
        self.__pencil_check.state = 'normal'
        self.__cartoon_check.state = 'normal'
        self.__summer_check.state = 'normal'
        self.__winter_check.state = 'normal'
        self.__gotham_check.state = 'normal'


    def add_action(self, action):
        '''This function add action if it is not in action list, else it removes it'''

        if action in self.__actions:
            self.__actions.remove(action)
        else:
            self.__actions.append(action)

        self.try_effects()

    def try_effects(self):
        '''This function apply each filter from actions to image'''

        if len(self.__back_images) != 0:
            if self.__back_images[self.__current_changes] is not None:
                self.__image_tmp = self.__back_images[self.__current_changes].copy()
                self.texture_to_image()

                for filter in self.__actions:
                    self.apply_filter(filter)


    '''
    Each of these functions add effect to actions,
    they have to be separated, because each of them is triggered 
    by radiobutton/ slider
    '''

    def apply_gray(self, *args):
        self.add_action(Filters.GRAY)

    def apply_sepia(self, *args):
        self.add_action(Filters.SEPIA)

    def apply_invert(self, *args):
        self.add_action(Filters.INVERT)

    def apply_brightness(self, *args):

        self.__brightness_slider.disabled = self.__brightness_check.state != 'down'

        self.add_action(Filters.BRIGHTNESS)

    def apply_darkness(self, *args):
        self.__darkness_slider.disabled = self.__darkness_check.state != 'down'

        self.add_action(Filters.DARKNESS)

    def apply_canny(self, *args):
        self.__canny_min.disabled = self.__canny_check.state != 'down'
        self.__canny_max.disabled = self.__canny_check.state != 'down'

        self.add_action(Filters.CANNY)

    def apply_correction(self, *args):
        self.add_action(Filters.CORRECTION)

    def apply_pencil(self, *args):
        self.add_action(Filters.PENCIL)

    def apply_cartoon(self, *args):
        self.add_action(Filters.CARTOON)

    def apply_summer(self, *args):
        self.add_action(Filters.SUMMER_EFFECT)

    def apply_winter(self, *args):
        self.add_action(Filters.WINTER_EFFECT)

    def apply_gotham(self, *args):
        self.add_action(Filters.GOTHAM_EFFECT)

    def activated_slider(self, *args):
        self.try_effects()


    def apply_filter(self, filter):
        #this function apply filter to image

        if filter == Filters.GRAY:
            if self.__gray_check.state == 'down':
                self.__image_tmp = filters.filter_to_gray(self.__image_tmp)
                self.__image_tmp = cv2.cvtColor(self.__image_tmp, cv2.COLOR_GRAY2BGR)

        elif filter == Filters.SEPIA:
            if self.__sepia_check.state == 'down':
                self.__image_tmp = filters.filter_sepia(self.__image_tmp)


        elif filter == Filters.INVERT:
            if self.__invert_check.state == 'down':
                self.__image_tmp = filters.invert(self.__image_tmp)


        elif filter == Filters.BRIGHTNESS:
            if self.__brightness_check.state == 'down':
                self.__image_tmp = filters.brightness(self.__image_tmp, self.__brightness_slider.value)
                # self.image_tmp = cv2.cvtColor(self.image_tmp, cv2.COLOR_RGB2BGR)

        elif filter == Filters.DARKNESS:
            if self.__darkness_check.state == 'down':
                self.__image_tmp = filters.darkness(self.__image_tmp, self.__darkness_slider.value)
                # self.image_tmp = cv2.cvtColor(self.image_tmp, cv2.COLOR_RGB2BGR)


        elif filter == Filters.CANNY:
            if self.__canny_check.state == 'down':
                self.__image_tmp = filters.filter_to_canny(self.__image_tmp, self.__canny_min.value, self.__canny_max.value)
                self.__image_tmp = cv2.cvtColor(self.__image_tmp, cv2.COLOR_RGB2BGR)

        elif filter == Filters.CORRECTION:
            if self.__correction_check.state == 'down':
                self.__image_tmp = filters.filter_gray_word_correction(self.__image_tmp)

        elif filter == Filters.PENCIL:
            if self.__pencil_check.state == 'down':
                self.__image_tmp = filters.filter_to_pencil_sketch(self.__image_tmp)
                self.__image_tmp = cv2.cvtColor(self.__image_tmp, cv2.COLOR_GRAY2BGR)

        elif filter == Filters.CARTOON:
            if self.__cartoon_check.state == 'down':
                self.__image_tmp = filters.filter_cartoon(self.__image_tmp)


        elif filter == Filters.SUMMER_EFFECT:
            if self.__summer_check.state == 'down':
                self.__image_tmp = filters.summer_effect(self.__image_tmp)


        elif filter == Filters.WINTER_EFFECT:
            if self.__winter_check.state == 'down':
                self.__image_tmp = filters.winter_effect(self.__image_tmp)


        elif filter == Filters.GOTHAM_EFFECT:
            if self.__gotham_check.state == 'down':
                self.__image_tmp = filters.gotham_filter(self.__image_tmp)

        self.texture_to_image()

    def texture_to_image(self):
        #this function allow to show image in kivy Image by transferring it from
        #cv2 standards to texture

        buffer = self.__image_tmp.tobytes()
        texture = Texture.create(size=(self.__image_tmp.shape[1], self.__image_tmp.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')

        self._image.texture = texture


    def set_path(self, filepath):
        #this function set path to read image from

        if filepath is not None:
            self.__path = filepath
            img = cv2.imread(filepath)
            img = cv2.flip(img, 0)

            self.__back_images.append(img.copy())
            self.__image_tmp = img.copy()

            self.texture_to_image()


    def navigate_back(self, *args):

        #unbind keyboard and it's actions to prevent
        #leak of functionality
        if platform != 'android' and platform != 'ios':
            self.__keyboard_closed()

        #function when back arrow is clicked
        App.get_running_app().screen_manager.navigate_to_Choose_file()

    def __keyboard_closed(self):
        if self._keyboard is not None:
            self._keyboard.unbind(on_key_down=self.on_keyboard_down)
            self._keyboard = None

    def keyboard_bind(self):
        #this will add ctrl + z combination for undo changes and ctrl + s for save image:
        if platform != 'android' and platform != 'ios':
            self._keyboard = Window.request_keyboard(self.__keyboard_closed, self)
            self._keyboard.bind(on_key_down=self.on_keyboard_down)

    '''
    Function below saves image not overriding original one.
    I could potentially ask user what name should be used, but I think
    in this app it has no use. Snap user don't care about name.
    It only has to look nice, and they want fast edit&upload functionality.
    And desktop users can easily edit if they want 
    '''
    def save_image(self, *args):

        file = os.path.splitext(self.__path)
        path = file[0]
        ext = file[1]
        image_to_save = self.__image_tmp.copy()
        image_to_save = cv2.flip(image_to_save, 0)

        current_time = time.strftime("%Y%m%d_%H%M%S")
        file_name = path + current_time.format(current_time) + ext
        cv2.imwrite(file_name, image_to_save)

        toast(self.__language.get('photo') + file_name + self.__language.get('saved_photo'))

    '''
    This function allows to undo change by clicking back arrow on editing tab or ctrl + z
    '''
    def undo_changes(self, *args):

        if self.__current_changes >= 1:
            self.reset_actions()
            self.__current_changes -= 1
            self.__back_images.pop()
            self.try_effects()
        else:
            toast(self.__language.get('no_changes_to_go_back'))

    '''
    This function allows to save changes so user can add more filters on top of that
    and use undo
    '''
    def save_changes(self, *args):
        self.__current_changes += 1
        self.__back_images.append(self.__image_tmp.copy())
        self.reset_actions()


    '''
    Functions to add undo and save functionality
    '''

    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        print(keycode)
        print(modifiers)
        if 'ctrl' in modifiers:
            #user clicked ctrl + z
            if keycode[0] == 122:
                self.undo_changes()
            elif keycode[0] == 115:
                self.save_image()



