import modules.scripts as scripts
import scripts.cc_const as const
import json
import os


STYLE_FILE = os.path.join(scripts.basedir(), "styles.json")

EMPTY_STYLE = {"styles": {}, "deleted": {}}


class StyleManager:
    def __init__(self):
        self.STYLE_SHEET = None

    def load_styles(self):
        if self.STYLE_SHEET is not None:
            return

        try:
            with open(STYLE_FILE, "r", encoding="utf-8") as json_file:
                self.STYLE_SHEET = json.loads(json_file.read())
                print("[Vec. CC] Style Sheet Loaded...")

        except IOError:
            with open(STYLE_FILE, "w+", encoding="utf-8") as json_file:
                self.STYLE_SHEET = EMPTY_STYLE
                json_file.write(json.dumps(self.STYLE_SHEET))
                print("[Vec. CC] Creating Empty Style Sheet...")

    def list_style(self):
        return list(self.STYLE_SHEET["styles"].keys())

    def get_style(self, style_name):
        try:
            style = self.STYLE_SHEET["styles"][style_name]
            return (
                style["alt"],
                style["brightness"],
                style["contrast"],
                style["saturation"],
                style["rgb"][0],
                style["rgb"][1],
                style["rgb"][2],
            )

        except KeyError:
            print(f'\n[Warning] No Style of Name "{style_name}" Found!\n')
            return (
                False,
                const.Brightness.default,
                const.Contrast.default,
                const.Saturation.default,
                const.COLOR.default,
                const.COLOR.default,
                const.COLOR.default,
            )

    def save_style(self, style_name, latent, bri, con, sat, r, g, b):
        if style_name in self.STYLE_SHEET["styles"].keys():
            print(f'\n[Warning] Duplicated Style Name "{style_name}" Detected! Values were not saved!\n')
            return self.list_style()

        style = {
            "alt": latent,
            "brightness": bri,
            "contrast": con,
            "saturation": sat,
            "rgb": [r, g, b],
        }

        self.STYLE_SHEET["styles"].update({style_name: style})

        with open(STYLE_FILE, "w+") as json_file:
            json_file.write(json.dumps(self.STYLE_SHEET))

        print(f'\nStyle of Name "{style_name}" Saved!\n')
        return self.list_style()

    def delete_style(self, style_name):
        try:
            style = self.STYLE_SHEET["styles"][style_name]
            self.STYLE_SHEET["deleted"].update({style_name: style})
            del self.STYLE_SHEET["styles"][style_name]

        except KeyError:
            print(f'\n[Warning] No Style of Name "{style_name}" Found!\n')
            return self.list_style()

        with open(STYLE_FILE, "w+") as json_file:
            json_file.write(json.dumps(self.STYLE_SHEET))

        print(f'\nStyle of Name "{style_name}" Deleted!\n')
        return self.list_style()
