from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem

from ChooseFile import ChooseFile
from Constants import PHOTO_SCREEN, EDITOR_SCREEN, CHOOSER_SCREEN

from PhotoEditor import PhotoEditor
from PhotoScreen import PhotoScreen


class HoneyScreenManager(ScreenManager):
    '''
    This class manages and performs switching screens
    '''

    def __init__(self):
        super(HoneyScreenManager, self).__init__()
        print("\nHoneyScreenManager.__init__():", id(self), "\n")

        #creating screens and naming them
        self.photo = PhotoScreen(name=PHOTO_SCREEN)
        self.photo_editor = PhotoEditor(name=EDITOR_SCREEN)
        self.chooser = ChooseFile(name=CHOOSER_SCREEN)

        self.add_widget(self.photo)
        self.add_widget(self.chooser)
        self.add_widget(self.photo_editor)

        self.current = PHOTO_SCREEN

    def navigate_to_Photo(self):
        #this navigates user to photo screen and start camera
        self.photo.start_camera()
        self.transition.direction = 'left'
        self.current = PHOTO_SCREEN

    def navigate_to_Choose_file(self):
        #this navigates user to choose file screen and stop camera
        self.photo.stop_camera()
        self.transition.direction = 'right'
        self.current = CHOOSER_SCREEN

    def navigate_to_photo_edit(self, filepath):
        #this navigates user to photo editor file screen and stop camera
        self.photo.stop_camera()
        self.transition.direction = 'left'
        self.photo_editor.set_path(filepath)
        self.current = EDITOR_SCREEN
