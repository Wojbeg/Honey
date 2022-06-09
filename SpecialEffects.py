from enum import Enum

class SpecialEffects(Enum):
    '''
    This class hold index of special effect card with
    image to display
    '''

    NORMAL = (-1, 'resources/images/empty_frame.png')
    SPACE = (0, "resources/images/space.jpg")
    DEVIL = (1, "resources/images/devil_horns.png")
    DOG = (2, "resources/images/dog.png")
    EYES = (3, "resources/images/funny_eyes.png")
    MESH = (4, "resources/images/mesh.png")
    # BUNNY
    # CROWN
    # HEARTS
    # FISH
    # AR_AVATAR

    #These above are most likely to be released in 1.1/1.2 app verion