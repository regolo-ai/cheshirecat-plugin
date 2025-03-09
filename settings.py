from cat.mad_hatter.decorators import plugin
from pydantic import BaseModel
from cat.looking_glass.cheshire_cat import MadHatter
import os
import json


class MySettings(BaseModel):
    regolo_key: str


@plugin
def settings_model():
    return MySettings


@plugin
def save_settings(settings):
    # Plugin settings are saved in the plugin folder
    # in a JSON file named "settings.json"
    plugin_path = os.path.dirname(os.path.realpath(__file__))
    settings_file_path = os.path.join(plugin_path, "settings.json")

    # Load already saved settings if the file exists; otherwise, use an empty dictionary
    if os.path.exists(settings_file_path):
        with open(settings_file_path, "r") as json_file:
            old_settings = json.load(json_file)
    else:
        old_settings = {}

    # Merge the old settings with the new ones
    updated_settings = {**old_settings, **settings}

    # Write the updated settings to the "settings.json" file in the plugin folder
    with open(settings_file_path, "w") as json_file:
        json.dump(updated_settings, json_file, indent=4)

    # Toggle the plugin to force settings reload
    madHatter = MadHatter()
    madHatter.toggle_plugin("cheshirecat_plugin")
    madHatter.toggle_plugin("cheshirecat_plugin")

    return updated_settings
