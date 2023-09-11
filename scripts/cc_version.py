import modules.scripts as scripts
import json

VERSION = 'v1.4.1'

def clean_outdated(EXT_NAME:str):
    with open(scripts.basedir() + '/' + 'ui-config.json', 'r') as json_file:
        configs = json.loads(json_file.read())

    cleaned_configs = {key: value for key, value in configs.items() if EXT_NAME not in key}

    with open(scripts.basedir() + '/' + 'ui-config.json', 'w') as json_file:
        json.dump(cleaned_configs, json_file)
