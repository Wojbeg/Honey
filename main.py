import os
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout
import Constants
import Strings
from HoneyScreenManager import HoneyScreenManager
from kivy import platform
from kivy.config import Config

'''
App is now in 1.0 alpha version and is available on desktop.
It has some code and functionality that would allow to work on
mobile platforms such as design or file management.

'''

'''
This app is not using kivy language, only python, because
app was produced as final python project.
It makes it sometimes a bit harder to write and read code.
Writing same with using combintation of python and kivy would 
allow
'''

'''
This settings allows us to make app work 
with fullscreen on mobile and other platforms

Third line allow to read and write configuration

These lines has to be in the same file as app
'''

Window.maximize()
Window.softinput_mode = "below_target"
Config.read('honey.ini')



class HoneyApp(MDApp):

    def build_config(self, config):
        '''
        Function read config file .ini with saved data
        '''

        self.__config = Config

        self.default_path = self.__config.getdefault(Constants.PATH, Constants.DEFAULT_PATH, None)
        if self.default_path is None:
            self.default_path = self.return_first_path()
            self.__config.setdefaults(Constants.PATH, {Constants.DEFAULT_PATH: self.default_path})


        self.number_of_detections = self.__config.getdefault(Constants.DETECTION, Constants.DEFAULT_DETECTION, None)
        if self.number_of_detections is None:
            self.number_of_detections = Constants.DEFAULT_DETECTION_VALUE
            self.__config.setdefaults(Constants.DETECTION, {Constants.DEFAULT_DETECTION: self.number_of_detections})

    def build(self):
        '''
        Standard kivy function on building app.
        Fist we set to dark mode (don't want user to burn eyes),
        create basic layout.
        Next screen manager is created and added - It allow user to switch screens
        on_drop_file override default window on drop file functionality with ours
        :returns whole layout
        '''

        '''
        Sometimes I left prints, user will not see them. These are 
        for developer only to know when screen is building or between what actions
        crash happen. Something like Logs in Android Studio.
        '''
        print("\nHoneyApp.build():", id(self), "\n")
        self.theme_cls.theme_style = "Dark"

        #As i said in other class for now I will stick with
        #only Polish version but it can easily be extended to other versions
        self.__language = Strings.STRINGS_PL

        self.__root = MDBoxLayout()
        self.__root.orientation = 'vertical'

        self.screen_manager = HoneyScreenManager()
        self.__root.add_widget(self.screen_manager)

        Window.bind(on_drop_file=self.on_drop_file)

        return self.__root

    def on_drop_file(self, window, filepath, *args):
        #
        # Function allow user to drag, drop and open photo to edit.
        # When correct type is dropped it app is navigated to editor
        # if incorrect app will show toast with specific information
        #

        filepath = filepath.decode('utf-8')
        filepath = filepath.replace("\\", "/")
        path = os.path.splitext(filepath)
        if path[1] not in Constants.Image_formats:
            toast(self.__language.get('wrong_image_type'))
        else:
            self.screen_manager.navigate_to_photo_edit(filepath)

    def return_first_path(self):
        #
        # This function returns path were user will be choosing files
        # to upload to app.
        # We can obtain desktop for limited platforms. And User want to choose
        # first from most accessible path which is desktop.
        #

        if platform == 'android':
            return Constants.DEFAULT_ROOT_PATH_ANDROID
        elif platform == 'win':
            return os.path.join(os.environ["HOMEPATH"], "Desktop")
        elif platform == 'linux':
            return os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
        else:
            return HoneyApp.user_data_dir

    def set_default_path(self, new_path):
        # function to set new default path
        self.__config.set(Constants.PATH, Constants.DEFAULT_PATH, new_path)
        self.__config.write()

    def set_default_num_of_detection(self, new_num_of_detecetion):
        # function to set new number of faces detection

        self.__config.set(Constants.DETECTION, Constants.DEFAULT_DETECTION, new_num_of_detecetion)
        self.__config.write()
        toast(self.__language.get('restart_to_apply'))

    def return_language(self):
        #it return app current language
        return self.__language

if __name__ == "__main__":
    HoneyApp().run()

