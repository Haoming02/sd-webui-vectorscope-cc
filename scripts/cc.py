from modules.sd_samplers_kdiffusion import KDiffusionSampler
import modules.scripts as scripts
from modules import shared
import gradio as gr
import torch
import json

def clean_outdated(EXT_NAME:str):
    with open(scripts.basedir() + '/' + 'ui-config.json', 'r') as json_file:
        configs = json.loads(json_file.read())

    cleaned_configs = {key: value for key, value in configs.items() if EXT_NAME not in key}

    with open(scripts.basedir() + '/' + 'ui-config.json', 'w') as json_file:
        json.dump(cleaned_configs, json_file)

class VectorscopeCC(scripts.Script):
    def __init__(self):
        clean_outdated('cc.py')

        global og_callback
        og_callback = KDiffusionSampler.callback_state

        global xyz_grid
        module_name = 'xyz_grid.py'
        for data in scripts.scripts_data:
            if data.script_class.__module__ == module_name and hasattr(data, "module"):
                xyz_grid = data.module
                break

        self.xyzCache = {}
        self.xyz_support()

    def xyz_support(self):
        def apply_field(field):
            def _(p, x, xs):
                self.xyzCache.update({field : x})
            return _

        def choices_bool():
            return ["True", "False"]

        def choices_method():
            return ["Default", "Uniform", "Cross", "Random", "Multi-Res"]

        extra_axis_options = [
            xyz_grid.AxisOption("[Vec.CC] Enable", str, apply_field("Enable"), choices=choices_bool),
            xyz_grid.AxisOption("[Vec.CC] Alt.", str, apply_field("Alt"), choices=choices_bool),
            xyz_grid.AxisOption("[Vec.CC] Skip", float, apply_field("Skip")),
            xyz_grid.AxisOption("[Vec.CC] Brightness", float, apply_field("Brightness")),
            xyz_grid.AxisOption("[Vec.CC] Contrast", float, apply_field("Contrast")),
            xyz_grid.AxisOption("[Vec.CC] Saturation", float, apply_field("Saturation")),
            xyz_grid.AxisOption("[Vec.CC] R", float, apply_field("R")),
            xyz_grid.AxisOption("[Vec.CC] G", float, apply_field("G")),
            xyz_grid.AxisOption("[Vec.CC] B", float, apply_field("B")),
            xyz_grid.AxisOption("[Adv.CC] Proc. H.Fix", str, apply_field("DoHR"), choices=choices_bool),
            xyz_grid.AxisOption("[Adv.CC] Method", str, apply_field("Method"), choices=choices_method)
        ]

        xyz_grid.axis_options.extend(extra_axis_options)

    def title(self):
        return "Vectorscope Color Correction"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        with gr.Accordion("Vectorscope CC", open=False):

            with gr.Row():
                enable = gr.Checkbox(label="Enable")
                latent = gr.Checkbox(label="Alt.")
                early = gr.Slider(label="Skip", minimum=0.0, maximum=1.0, step=0.1, value=0.0)

            with gr.Row():
                bri = gr.Slider(label="Brightness", minimum=-5.0, maximum=5.0, step=0.1, value=0.0)
                con = gr.Slider(label="Contrast", minimum=0.5, maximum=1.5, step=0.05, value=1.0)
                sat = gr.Slider(label="Saturation", minimum=0.5, maximum=1.5, step=0.05, value=1.0)

            with gr.Row():
                r = gr.Slider(label="R", info='Cyan | Red', minimum=-2.5, maximum=2.5, step=0.05, value=0.0)
                g = gr.Slider(label="G", info='Magenta | Green',minimum=-2.5, maximum=2.5, step=0.05, value=0.0)
                b = gr.Slider(label="B", info='Yellow | Blue',minimum=-2.5, maximum=2.5, step=0.05, value=0.0)

            with gr.Accordion("Advanced Settings", open=False):
                doHR = gr.Checkbox(label="Process Hires. fix")
                method = gr.Radio(["Default", "Uniform", "Cross", "Random", "Multi-Res"], label="Noise Settings", value="Default")

        return [enable, latent, bri, con, sat, early, r, g, b, doHR, method]

    def parse_bool(self, string:str):
        if string.lower() == "true":
            return True
        if string.lower() == "false":
            return False
        
        raise ValueError(f"Invalid Value: {string}")

    def process(self, p, enable:bool, latent:bool, bri:float, con:float, sat:float, early:float, r:float, g:float, b:float, doHR:bool, method:str):
        if 'Enable' in self.xyzCache.keys():
            enable = self.parse_bool(self.xyzCache['Enable'])

        if not enable:
            if 'Enable' not in self.xyzCache.keys():
                if len(self.xyzCache) > 0:
                    print('\n\n[X/Y/Z Plot] x [Vec.CC] Extension is not Enabled!\n\n')
                self.xyzCache.clear()

            KDiffusionSampler.callback_state = og_callback
            return p

        for k, v in self.xyzCache.items():
            match k:
                case 'Alt':
                    latent = self.parse_bool(v)
                case 'Brightness':
                    bri = v
                case 'Contrast':
                    con = v
                case 'Saturation':
                    sat = v
                case 'Skip':
                    early = v
                case 'R':
                    r = v
                case 'G':
                    g = v
                case 'B':
                    b = v
                case 'DoHR':
                    doHR = self.parse_bool(v)
                case 'Method':
                    print('This setting currently does nothing!')

        self.xyzCache.clear()

        steps = p.steps
        if not hasattr(p, 'enable_hr') and hasattr(p, 'denoising_strength') and not shared.opts.img2img_fix_steps:
            steps = int(steps * p.denoising_strength)

        stop = steps * (1.0 - early)

        if stop < 1:
            return p

        bri /= steps
        con = pow(con, 1.0 / steps)
        sat = pow(sat, 1.0 / steps)
        r /= steps
        g /= steps
        b /= steps

        mode = 'x' if latent else 'denoised'

        # Channel 0:    Dark    |   Bright
        # Channel 1:    Purple  |   Green
        # Channel 2:    Red     |   Cyan
        # Channel 2:    Violet  |   Yellow

        def callback_state(self, d):
            if not doHR:
                if hasattr(p, 'enable_hr') and p.enable_hr:
                    if not hasattr(p, 'hr_pass'):
                        p.hr_pass = 0

                    if p.hr_pass == 0:
                        if d["i"] == 0:
                            p.hr_pass = 1

                    elif p.hr_pass == 1:
                        if d["i"] == 0:
                            p.hr_pass = 2

                    if p.hr_pass == 2:
                        return og_callback(self, d)

            if d["i"] > stop:
                return og_callback(self, d)

            batchSize = d[mode].size(0)

            for i in range(batchSize):
                BRIGHTNESS = d[mode][i, 0]
                R = d[mode][i, 2]
                G = d[mode][i, 1]
                B = d[mode][i, 3]

                BRIGHTNESS += torch.abs(BRIGHTNESS) * bri
                BRIGHTNESS *= con

                R -= torch.abs(R) * r
                G += torch.abs(G) * g
                B -= torch.abs(B) * b

                R *= sat
                G *= sat
                B *= sat

            return og_callback(self, d)

        KDiffusionSampler.callback_state = callback_state
        return p

    def postprocess_image(self, p, *args):
        if hasattr(p, 'hr_pass'):
            del p.hr_pass

    def postprocess(self, p, processed, *args):
        KDiffusionSampler.callback_state = og_callback
