from modules.script_callbacks import on_ui_settings
from modules.shared import OptionInfo, opts


def settings():
    opts.add_option(
        "cc_metadata",
        OptionInfo(
            True,
            "Append Vectorscope CC parameters to generation information",
            section=("infotext", "Infotext"),
        ),
    )


on_ui_settings(settings)
