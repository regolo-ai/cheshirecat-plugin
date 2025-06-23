import os
import json

from cat.mad_hatter.decorators import plugin
from pydantic import BaseModel
from cat.looking_glass.cheshire_cat import MadHatter

# Plugin settings are saved in the plugin folder
# in a JSON file named "settings.json"
PLUGIN_PATH = os.path.dirname(os.path.realpath(__file__))
SETTINGS_FILE_PATH = os.path.join(PLUGIN_PATH, "settings.json")


class MySettings(BaseModel):
    regolo_key: str


@plugin
def settings_model():
    return MySettings


@plugin
def save_settings(settings):
    # Load already saved settings if the file exists; otherwise, use an empty dictionary
    old_settings = load_settings(SETTINGS_FILE_PATH)

    # Merge the old settings with the new ones
    updated_settings = {**old_settings, **settings}

    # Write the updated settings to the "settings.json" file in the plugin folder
    with open(SETTINGS_FILE_PATH, "w") as json_file:
        json.dump(updated_settings, json_file, indent=4)  # noqa

    # Toggle the plugin to force settings reload
    madHatter = MadHatter()
    madHatter.toggle_plugin("cheshirecat_plugin")
    madHatter.toggle_plugin("cheshirecat_plugin")

    return updated_settings

def load_env_settings():
    return MySettings(regolo_key=os.getenv("REGOLO_KEY"))

def load_settings(path):
    # Load already saved settings if the file exists; otherwise, use an empty dictionary
    if os.path.exists(path):
        with open(path, "r") as json_file:
            settings_dict = json.load(json_file)
            return MySettings(**settings_dict)
    else:
        return load_env_settings()