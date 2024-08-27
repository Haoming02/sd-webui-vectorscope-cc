from modules import scripts
import gradio as gr
import json
import os


STYLE_FILE = os.path.join(scripts.basedir(), "styles.json")

EMPTY_STYLE = {"styles": {}, "deleted": {}}


class StyleManager:
    def __init__(self):
        self.STYLE_SHEET = None

    def load_styles(self):
        if os.path.isfile(STYLE_FILE):
            with open(STYLE_FILE, "r", encoding="utf-8") as json_file:
                self.STYLE_SHEET = json.load(json_file)
                print("[Vec. CC] Style Sheet Loaded...")

        else:
            with open(STYLE_FILE, "w+", encoding="utf-8") as json_file:
                self.STYLE_SHEET = EMPTY_STYLE
                json.dump(self.STYLE_SHEET, json_file)
                print("[Vec. CC] Creating Empty Style Sheet...")

        return self.list_style()

    def list_style(self):
        return list(self.STYLE_SHEET["styles"].keys())

    def get_style(self, style_name: str):
        style: dict = self.STYLE_SHEET["styles"].get(style_name, None)

        if not style:
            print(f'\n[Error] No Style of name "{style_name}" was found!\n')
            return [gr.update()] * 12

        return (
            style.get("alt", gr.update()),
            style.get("brightness", gr.update()),
            style.get("contrast", gr.update()),
            style.get("saturation", gr.update()),
            *style.get("rgb", (gr.update(), gr.update(), gr.update())),
            style.get("hr", gr.update()),
            style.get("ad", gr.update()),
            style.get("rn", gr.update()),
            style.get("noise", gr.update()),
            style.get("scaling", gr.update()),
        )

    def save_style(
        self,
        style_name: str,
        latent: bool,
        bri: float,
        con: float,
        sat: float,
        r: float,
        g: float,
        b: float,
        hr: bool,
        ad: bool,
        rn: bool,
        noise: str,
        scaling: str,
    ):
        if style_name in self.STYLE_SHEET["styles"]:
            print(f'\n[Error] Duplicated Style Name: "{style_name}" Detected!')
            print("Values were not saved!\n")
            return self.list_style()

        new_style = {
            "alt": latent,
            "brightness": bri,
            "contrast": con,
            "saturation": sat,
            "rgb": [r, g, b],
            "hr": hr,
            "ad": ad,
            "rn": rn,
            "noise": noise,
            "scaling": scaling,
        }

        self.STYLE_SHEET["styles"].update({style_name: new_style})

        with open(STYLE_FILE, "w+") as json_file:
            json.dump(self.STYLE_SHEET, json_file)

        print(f'\nStyle of Name "{style_name}" Saved!\n')
        return self.list_style()

    def delete_style(self, style_name: str):
        if style_name not in self.STYLE_SHEET["styles"]:
            print(f'\n[Error] No Style of name "{style_name}" was found!\n')
            return self.list_style()

        style: dict = self.STYLE_SHEET["styles"].get(style_name)
        self.STYLE_SHEET["deleted"].update({style_name: style})
        del self.STYLE_SHEET["styles"][style_name]

        with open(STYLE_FILE, "w+") as json_file:
            json.dump(self.STYLE_SHEET, json_file)

        print(f'\nStyle of name "{style_name}" was deleted!\n')
        return self.list_style()
