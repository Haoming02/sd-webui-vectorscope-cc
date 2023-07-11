from modules import script_callbacks, shared

def on_ui_settings():
    shared.opts.add_option("cc_metadata", shared.OptionInfo(False, "Add Vectorscope CC parameters to generation information", section=("infotext", "Infotext")))

script_callbacks.on_ui_settings(on_ui_settings)
