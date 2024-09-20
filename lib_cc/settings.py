from modules.shared import OptionInfo, opts
from modules import scripts
from json import load, dump
import os

section = ("cc", "Vectorscope CC")


def settings():
    opts.add_option(
        "cc_metadata",
        OptionInfo(
            True,
            "Append Vectorscope CC parameters to generation information",
            section=section,
            category_id="sd",
        ),
    )

    opts.add_option(
        "cc_no_defaults",
        OptionInfo(
            True,
            'Add the "do_not_save_to_config" flag to all components',
            section=section,
            category_id="sd",
            onchange=reset_ui_config,
        )
        .needs_reload_ui()
        .info(
            "uncheck this option if you wish to use the built-in Defaults function) (enable this option again if the extension is not functioning correctly after an update"
        ),
    )


def reset_ui_config():
    extension = "cc.py"
    ui_config = os.path.join(scripts.basedir(), "ui-config.json")

    with open(ui_config, "r", encoding="utf-8") as json_file:
        configs = load(json_file)

    cleaned_configs = {
        key: value for key, value in configs.items() if extension not in key
    }

    with open(ui_config, "w", encoding="utf-8") as json_file:
        dump(cleaned_configs, json_file)
