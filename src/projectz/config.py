"""
This module handles the configuration for the game.
"""

import configparser
from pathlib import Path
import xdg.BaseDirectory

CONFIG_DIR = Path(xdg.BaseDirectory.save_config_path("projectz"))
CONFIG_FILE = CONFIG_DIR / "config.ini"


def create_default_config():
    """
    Creates a default configuration file.
    """
    config = configparser.ConfigParser()

    config["screen"] = {
        "width": "800",
        "height": "600",
        "fullscreen": "false",
    }

    config["audio"] = {
        "sound_on": "true",
        "volume": "0.5",
    }

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    with open(CONFIG_FILE, "w") as f:
        config.write(f)


def get_config():
    """
    Loads the configuration.

    If no config file exists, a default one is created.

    Returns:
        The configuration object.
    """
    if not CONFIG_FILE.is_file():
        create_default_config()

    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return config


config = get_config()
