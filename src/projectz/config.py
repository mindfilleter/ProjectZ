import configparser
import xdg.BaseDirectory

# 1. Configuration Setup
CONFIG_DIR = xdg.BaseDirectory.save_config_path("projectz")
CONFIG_FILE = f"{CONFIG_DIR}/config.ini"


def create_default_config():
    """Creates a default configuration file if one does not already exist."""
    config = configparser.ConfigParser()

    # Screen Settings
    config["screen"] = {
        "width": "800",
        "height": "600",
        "fullscreen": "false",
    }

    # Audio Settings
    config["audio"] = {
        "sound_on": "true",
        "volume": "0.5",
    }

    # Write the configuration to the file
    with open(CONFIG_FILE, "w") as f:
        config.write(f)


def get_config():
    """
    Loads the configuration from the user's config directory.
    If no config file exists, a default one is created.
    """
    # Create a default config if necessary
    if not xdg.BaseDirectory.load_config_paths("projectz/config.ini"):
        create_default_config()

    # Load the configuration
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return config


# 2. Main Configuration Object (to be imported by other modules)
config = get_config()
