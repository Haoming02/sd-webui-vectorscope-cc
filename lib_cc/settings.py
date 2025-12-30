from modules.shared import OptionInfo, opts
from modules import scripts
from json import load, dump
from gradio import Slider
import os

section = ("cc", "Vectorscope CC")


def settings():
    opts.add_option(
        "cc_metadata",
        OptionInfo(
            True,
            "Append Vectorscope CC parameters to generation infotext",
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
        .info("disable this option if you wish to use the built-in Defaults feature")
        .info("enable again if the extension is not working correctly after an update")
        .needs_reload_ui(),
    )

    opts.add_option(
        "cc_rand_method",
        OptionInfo(
            False,
            "Randomize the Noise Settings as well",
            section=section,
            category_id="sd",
        ),
    )

    opts.add_option(
        "cc_rand_scaling",
        OptionInfo(
            False,
            "Randomize the Scaling Settings as well",
            section=section,
            category_id="sd",
        ),
    )

    for lbl, minVal, maxVal in [
        ("Brightness", (-5.0, 0.0), (0.0, 5.0)),
        ("Contrast", (-5.0, 0.0), (0.0, 5.0)),
        ("Saturation", (0.25, 1.0), (1.0, 1.75)),
        ("Color", (-4.0, 0.0), (0.0, 4.0)),
    ]:

        opts.add_option(
            f"cc_{lbl.lower()}_min",
            OptionInfo(
                minVal[0],
                f"{lbl} - Min",
                Slider,
                {"step": 0.05, "minimum": minVal[0], "maximum": minVal[1]},
                section=section,
                category_id="sd",
            ).needs_reload_ui(),
        )

        opts.add_option(
            f"cc_{lbl.lower()}_max",
            OptionInfo(
                maxVal[1],
                f"{lbl} - Max",
                Slider,
                {"step": 0.05, "minimum": maxVal[0], "maximum": maxVal[1]},
                section=section,
                category_id="sd",
            ).needs_reload_ui(),
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
