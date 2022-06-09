'''
This dictionary will hold Polish language data.
It's goal is to mimic android version of strings.xml,
but the goal was to use most of python.
Same convention as in mobile development, same name
of string in every language, different value.
If we want to extend app to other languages, we simpy
create new dictionary with all same keys but different values like, and
add some settings pannel to switch them.
STRINGS_EN = { 'wrong_image_type': "Invalid file format. Only images are allowed!" ...}
'''

STRINGS_PL = {
    'wrong_image_type': "Niedopuszczalny typ pliku. Tylko obrazy są dopuszczalne!",
    'choose_folder': "Wybierz folder",
    'choose_edit_photo': "Przeglądaj swoje zdjęcia i wybierz jeśli chcesz jakieś edytować",
    'choose_main_folder': "Wybierz domyślny folder",
    'choose_image': 'Wybierz obraz do edycji',
    'edit_photo': 'Edytuj zdjęcie',
    'edit_photo_with_effects': "Edytuj zdjęcie efektami",
    'min': "Min:",
    'max': "Max:",
    'photo': "Zdjęcie ",
    'saved_photo': " zostało zapisane ;)",
    'restart_to_apply': "Żeby dane się zaktualizowały zrestartuj aplikacje",
    'num_to_detect': "Zmień max twarzy",
    'max_detection': "Max wykrywania:"
}