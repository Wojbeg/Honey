import os
import os.path
from kivy.app import App
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from kivymd.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRoundFlatIconButton, MDRaisedButton, MDTextButton, MDFlatButton, MDFillRoundFlatButton
from kivymd.uix.dropdownitem import MDDropDownItem
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.toolbar import MDToolbar
from Constants import Image_formats, MAX_DETECTION_VALUE, MIN_DETECTION_VALUE
from Strings import STRINGS_PL


class ChooseFile(Screen):
    '''
    This class allow users to choose image to edit,
    and set default folder and numer of faces
    '''
    def __init__(self, **kwargs):
        super(ChooseFile, self).__init__(**kwargs)
        print("\nChooseFile.__init__():", id(self), "\n")

        self.__path = App.get_running_app().default_path

        self.__language = App.get_running_app().return_language()

        #bind keyboard events for mobile
        Window.bind(on_keyboard=self.events)

        #create main layout
        self.__layout = MDBoxLayout()
        self.__layout.orientation = 'vertical'

        self.add_widget(self.__layout)

        #toolbar
        self.__toolbar = MDToolbar()

        self.__toolbar.title = self.__language.get('choose_folder')
        self.__toolbar.right_action_items = [['arrow-right-thick', lambda x: self.back_btn(x)]]
        self.__toolbar.elevation = 10

        self.__layout.add_widget(self.__toolbar)

        #float layout under toolbar
        self.__float = MDFloatLayout()
        self.__layout.add_widget(self.__float)

        #label with top text
        self.__screen_label = MDLabel()
        self.__screen_label.text = self.__language.get('choose_edit_photo')
        self.__screen_label.halign = "center"
        self.__screen_label.font_style = 'Subtitle1'
        self.__screen_label.pos_hint = {'center_x': .5, 'center_y': 0.95}


        #button to select new direcotry
        self.__select_dir_button = MDRoundFlatIconButton()
        self.__select_dir_button.text = self.__language.get('choose_main_folder')
        self.__select_dir_button.icon = "folder"
        self.__select_dir_button.pos_hint = {'center_x': 0.5, 'center_y': .4}
        self.__select_dir_button.on_release = self.dir_manager_open

        #button to select image to edit
        self.__select_image_button = MDRoundFlatIconButton()
        self.__select_image_button.text = self.__language.get('choose_image')
        self.__select_image_button.icon = 'image-edit'
        self.__select_image_button.pos_hint = {'center_x': 0.5, 'center_y': .3}
        self.__select_image_button.on_release = self.img_manager_open


        self.__float.add_widget(self.__screen_label)
        self.__float.add_widget(self.__select_dir_button)
        self.__float.add_widget(self.__select_image_button)

        #variable to check if dir manager is opened
        self.__dir_manager_open = False

        #creating directory manager
        self.__dir_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=True,
            search='dirs'
        )

        #same as above but for image manager
        self.__img_manager_open = False

        self.__img_manager = MDFileManager(
            exit_manager=self.img_exit_manager,
            select_path=self.img_select_path,
            preview=True,
            search='all'
        )

        #creating dropdown section for choosing new value of face detecion
        self.__dropdown_box = MDBoxLayout()
        self.__dropdown_box.orientation = 'horizontal'
        self.__dropdown_box.pos_hint = {'center_x': 0.5, 'center_y': 0.2}
        self.__dropdown_box.size_hint_x = 0.2

        self.__choose_faces = MDLabel(text=self.__language.get('max_detection'))
        self.__choose_faces.size_hint_x = 0.8
        self.__dropdown_box.add_widget(self.__choose_faces)

        self.__max_detection_value_label = MDLabel(text='')
        self.__max_detection_value_label.size_hint_x = 0.1
        self.get_number_of_detection()
        self.__dropdown_box.add_widget(self.__max_detection_value_label)

        #creating numbers of max text
        self.__menu_items = [
            {
                "text": f"{i}",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=i: self.dropdown_detection_callback(x),
            } for i in range(MIN_DETECTION_VALUE, MAX_DETECTION_VALUE+1)
        ]

        #creating button for showing dropdown menu
        self.__detection_button = MDFlatButton()
        self.__detection_button.text = self.__language.get('num_to_detect')
        self.__detection_button.pos_hint = {'center_x': 0.5, 'center_y': 0.1}
        self.__detection_button.size_hint_x = 0.1
        self.__detection_button.size_hint_y = 0.1

        self.__float.add_widget(self.__detection_button)

        self.__detection_menu = MDDropdownMenu(
            caller=self.__detection_button,
            items=self.__menu_items,
            width_mult=4,
        )

        self.__detection_button.on_release = self.__detection_menu.open

        self.__float.add_widget(self.__dropdown_box)

    def get_number_of_detection(self):
        #This function get default number of detection
        detection = App.get_running_app().number_of_detections
        self.__max_detection_value_label.text = str(detection)
        return detection

    def dropdown_detection_callback(self, new_detection):
        #This function will set new
        App.get_running_app().set_default_num_of_detection(new_detection)
        self.__max_detection_value_label.text = str(new_detection)

    def back_btn(self, button):
        # It will navigate back to photo screen
        App.get_running_app().screen_manager.navigate_to_Photo()

    def dir_manager_open(self):
        # Opnens manager with dirs to choose from
        self.__dir_manager.show(self.__path)  # output manager to the screen
        self.__dir_manager_open = True

    def select_path(self, path):
        '''It will be called when you click on the file name
        or the catalog selection button.

        :type path: str;
        :param path: path to the selected directory or file;
        '''

        self.__path = path
        self.exit_manager()
        toast(path)
        App.get_running_app().set_default_path(path)


    def exit_manager(self, *args):
        '''Called when the user reaches the root of the directory tree.'''

        self.__dir_manager_open = False
        self.__dir_manager.close()

    def img_manager_open(self):
        '''It open image manager '''
        self.__img_manager.show(self.__path)  # output manager to the screen
        self.__img_manager_open = True

    def img_select_path(self, filepath):
        '''It allows user to choose other file, without changing default save/read path'''

        filepath = filepath.replace("\\", "/")
        path = os.path.splitext(filepath)
        if path[1] not in Image_formats:
            toast(self.__language.get('wrong_image_type'))
        else:
            self.img_exit_manager()
            App.get_running_app().screen_manager.navigate_to_photo_edit(filepath)

    def img_exit_manager(self, *args):
        '''It close image chooser manager.'''
        self.__img_manager_open = False
        self.__img_manager.close()

    def events(self, instance, keyboard, keycode, text, modifiers):
        '''Called when buttons are pressed on the mobile device'''

        if keyboard in (1001, 27):
            if self.__dir_manager_open:
                self.__dir_manager.back()
            elif self.__img_manager_open:
                self.__img_manager.back()
        return True