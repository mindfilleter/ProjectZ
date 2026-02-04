from importlib import resources

from pygame import image
from pygame import mixer
from pygame import surface


def get_image(image_name: str) -> surface.Surface:
    with resources.path("projectz.assets", image_name) as path:
        return image.load(path).convert_alpha()


def get_sound(sound_name: str) -> mixer.Sound:
    with resources.path("projecctz.assets", sound_name) as path:
        return mixer.Sound(path)
