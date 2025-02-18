from enum import Enum
from cat.mad_hatter.decorators import plugin
from pydantic import BaseModel, Field, field_validator
from cat.looking_glass.cheshire_cat import MadHatter
from cat.looking_glass.cheshire_cat import CheshireCat
import os
import json

class MySettings(BaseModel):
    regolo_key: str

@plugin
def settings_model():
    return MySettings

@plugin
def save_settings(settings):
    # by default, plugin settings are saved inside the plugin folder
    #   in a JSON file called settings.json
    ccat = CheshireCat()
    madHatter = MadHatter()
    plugin = ccat.mad_hatter.get_plugin()
    settings_file_path = os.path.join(plugin._path, "settings.json")

        # load already saved settings
    old_settings = plugin.load_settings()

        # overwrite settings over old ones
    updated_settings = {**old_settings, **settings}

        # write settings.json in plugin folder
    with open(settings_file_path, "w") as json_file:
        json.dump(updated_settings, json_file, indent=4)
    madHatter.toggle_plugin("cheshirecat_plugin")
    madHatter.toggle_plugin("cheshirecat_plugin")
    return updated_settings