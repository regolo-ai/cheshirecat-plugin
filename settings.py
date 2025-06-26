import os
import json

from cat.mad_hatter.decorators import plugin
from pydantic import BaseModel
from cat.looking_glass.cheshire_cat import MadHatter
from cat.log import log

# Plugin settings are saved in the plugin folder
# in a JSON file named "settings.json"
plugin_path = os.path.dirname(os.path.realpath(__file__))
settings_file_path = os.path.join(plugin_path, "settings.json")

class MySettings(BaseModel):
    regolo_key: str

class EmptySettings(BaseModel):
    pass


if os.getenv("REGOLO_KEY"):
    @plugin
    def settings_model():
        log.critical("test1")
        return EmptySettings
else:
    @plugin
    def settings_model():
        log.critical("test2")
        return MySettings

@plugin
def save_settings(settings):
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
        json.dump(updated_settings, json_file, indent=4)  # noqa

    # Toggle the plugin to force settings reload
    madHatter = MadHatter()
    madHatter.toggle_plugin("cheshirecat_plugin")
    madHatter.toggle_plugin("cheshirecat_plugin")

    return updated_settings