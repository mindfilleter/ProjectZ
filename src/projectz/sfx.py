"""
This module contains a helper for playing sound effects.
"""

from importlib import resources
from typing import Dict

from pygame import mixer

from projectz.logger import logger


class SoundEffects:
    def __init__(self):
        self.sfx: Dict[str, mixer.Sound] = {}

    def load_sfx(self, name):
        with resources.path("projectz.assets", name) as sfx_path:
            self.sfx[name] = mixer.Sound(sfx_path)

    def play_sfx(self, name):
        self.sfx[name].play(0)

    def unload_sfx(self, name):
        del self.sfx[name]

    def unload_all_sfx(self):
        self.sfx.clear()


SFX = ["attack.mp3"]

sound_effects = SoundEffects()


def load_sound_effects():
    global sound_effects
    for sfx_name in SFX:
        logger.debug(f"Loading {sfx_name}")
        sound_effects.load_sfx(sfx_name)


def play_sfx(name):
    sound_effects.play_sfx(name)
