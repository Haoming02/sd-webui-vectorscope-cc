from modules import script_callbacks
import modules.scripts as scripts
import json

VERSION = 'v2.0.1'

def clean_outdated(EXT_NAME:str):
    with open(scripts.basedir() + '/' + 'ui-config.json', 'r', encoding='utf8') as json_file:
        configs = json.loads(json_file.read())

    cleaned_configs = {key: value for key, value in configs.items() if EXT_NAME not in key}

    with open(scripts.basedir() + '/' + 'ui-config.json', 'w', encoding='utf8') as json_file:
        json.dump(cleaned_configs, json_file)

def refresh_sliders():
    clean_outdated('cc.py')
    clean_outdated('cc_hdr.py')

script_callbacks.on_before_ui(refresh_sliders)
