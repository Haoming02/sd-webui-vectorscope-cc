from modules.sd_samplers_kdiffusion import KDiffusionSampler
import modules.scripts as scripts
from modules import shared
import gradio as gr
import random

from scripts.cc_noise import *

from scripts.cc_version import VERSION
from scripts.cc_version import clean_outdated

from scripts.cc_colorpicker import create_colorpicker
from scripts.cc_colorpicker import horizontal_js
from scripts.cc_colorpicker import vertical_js

from scripts.cc_style import StyleManager
style_manager = StyleManager()
style_manager.load_styles()

og_callback = KDiffusionSampler.callback_state

class VectorscopeCC(scripts.Script):
    def __init__(self):
        clean_outdated('cc.py')

        self.xyzCache = {}
        self.xyz_support()

    def xyz_support(self):
        def apply_field(field):
            def _(p, x, xs):
                self.xyzCache.update({field : x})
            return _

        def choices_bool():
            return ["False", "True"]

        def choices_method():
            return ["Disabled", "Straight", "Straight Abs.", "Cross", "Cross Abs.", "Ones", "N.Random", "U.Random", "Multi-Res", "Multi-Res Abs."]

        for data in scripts.scripts_data:
            if data.script_class.__module__ == 'xyz_grid.py' and hasattr(data, "module"):
                xyz_grid = data.module
                break

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
            xyz_grid.AxisOption("[Adv.CC] Method", str, apply_field("Method"), choices=choices_method),
            xyz_grid.AxisOption("[Adv.CC] Randomize", int, apply_field("Random"))
        ]

        xyz_grid.axis_options.extend(extra_axis_options)

    def title(self):
        return "Vectorscope Color Correction"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):

        with gr.Accordion(f"Vectorscope CC {VERSION}", open=False):

            with gr.Row():
                enable = gr.Checkbox(label="Enable")
                latent = gr.Checkbox(label="Alt.")
                early = gr.Slider(label="Skip", minimum=0.0, maximum=1.0, step=0.1, value=0.0)

            with gr.Row():
                bri = gr.Slider(label="Brightness", minimum=-5.0, maximum=5.0, step=0.1, value=0.0)
                con = gr.Slider(label="Contrast", minimum=0.5, maximum=1.5, step=0.05, value=1.0)
                sat = gr.Slider(label="Saturation", minimum=0.5, maximum=1.5, step=0.05, value=1.0)

            with gr.Row():
                with gr.Column():
                    r = gr.Slider(label="R", info='Cyan | Red', minimum=-2.5, maximum=2.5, step=0.05, value=0.0)
                    g = gr.Slider(label="G", info='Magenta | Green',minimum=-2.5, maximum=2.5, step=0.05, value=0.0)
                    b = gr.Slider(label="B", info='Yellow | Blue',minimum=-2.5, maximum=2.5, step=0.05, value=0.0)
                
                create_colorpicker(is_img2img)

                for component in [r, g, b]:
                    component.change(None, inputs=[r, g, b], outputs=[], _js=horizontal_js(is_img2img))
                    component.change(None, inputs=[r, g, b], outputs=[], _js=vertical_js(is_img2img))

            with gr.Accordion("Styles", open=False):
                
                with gr.Row():
                    with gr.Column():
                        style_choice = gr.Dropdown(label="Styles", choices=style_manager.list_style())
                        style_name = gr.Textbox(label="Style Name")

                    with gr.Column():
                        with gr.Row(variant="compact"):
                            apply_btn = gr.Button(value="Apply Style")
                            refresh_btn = gr.Button(value="Refresh Style")
                        with gr.Row(variant="compact"):
                            save_btn = gr.Button(value="Save Style")
                            delete_btn = gr.Button(value="Delete Style")

                    apply_btn.click(fn=style_manager.get_style, inputs=style_choice, outputs=[latent, bri, con, sat, r, g, b])
                    save_btn.click(fn=lambda *args: gr.update(choices=style_manager.save_style(*args)), inputs=[style_name, latent, bri, con, sat, r, g, b], outputs=style_choice)
                    delete_btn.click(fn=lambda name: gr.update(choices=style_manager.delete_style(name)), inputs=style_name, outputs=style_choice)
                    refresh_btn.click(fn=lambda _: gr.update(choices=style_manager.list_style()), outputs=style_choice)


            with gr.Accordion("Advanced Settings", open=False):
                doHR = gr.Checkbox(label="Process Hires. fix")
                method = gr.Radio(["Straight", "Straight Abs.", "Cross", "Cross Abs.", "Ones", "N.Random", "U.Random", "Multi-Res", "Multi-Res Abs."], label="Noise Settings", value="Straight Abs.")

            with gr.Row():
                reset_btn = gr.Button(value="Reset")
                self.register_reset(reset_btn, enable, latent, bri, con, sat, early, r, g, b, doHR, method)

                random_btn = gr.Button(value="Randomize")
                self.register_random(random_btn, bri, con, sat, r, g, b)

        return [enable, latent, bri, con, sat, early, r, g, b, doHR, method]

    def register_reset(self, reset_btn, enable, latent, bri, con, sat, early, r, g, b, doHR, method):
        for component in [enable, latent, doHR]:
            reset_btn.click(fn=lambda _: gr.update(value=False), outputs=component)
        for component in [early, bri, r, g, b]:
            reset_btn.click(fn=lambda _: gr.update(value=0.0), outputs=component)
        for component in [con, sat]:
            reset_btn.click(fn=lambda _: gr.update(value=1.0), outputs=component)

        reset_btn.click(fn=lambda _: gr.update(value='Straight Abs.'), outputs=method)

    def register_random(self, random_btn, bri, con, sat, r, g, b):
        for component in [bri, r, g, b]:
            random_btn.click(fn=lambda _: gr.update(value=round(random.uniform(-2.5, 2.5), 2)), outputs=component)
        for component in [con, sat]:
            random_btn.click(fn=lambda _: gr.update(value=round(random.uniform(0.5, 1.5), 2)), outputs=component)

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

        if 'Random' in self.xyzCache.keys():
            print('\n\n[X/Y/Z Plot] x [Vec.CC] Randomize is Enabled!')
            if len(self.xyzCache) > 1:
                print('Some settings will not apply!')

        cc_seed = None

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
                    method = v
                case 'Random':
                    cc_seed = v

        self.xyzCache.clear()

        if method == 'Disabled':
            KDiffusionSampler.callback_state = og_callback
            return p

        steps = p.steps
        if not hasattr(p, 'enable_hr') and hasattr(p, 'denoising_strength') and not shared.opts.img2img_fix_steps:
            steps = int(steps * p.denoising_strength)

        stop = steps * (1.0 - early)

        if cc_seed is not None:
            random.seed(cc_seed)

            bri = round(random.uniform(-2.5, 2.5), 2)
            r = round(random.uniform(-2.5, 2.5), 2)
            g = round(random.uniform(-2.5, 2.5), 2)
            b = round(random.uniform(-2.5, 2.5), 2)

            con = round(random.uniform(0.5, 1.5), 2)
            sat = round(random.uniform(0.5, 1.5), 2)

            print(f'-> Seed: {cc_seed}')
            print(f'Brightness:\t{bri}')
            print(f'Contrast:\t{con}')
            print(f'Saturation:\t{sat}')
            print(f'R:\t\t{r}')
            print(f'G:\t\t{g}')
            print(f'B:\t\t{b}\n')

        if stop < 1:
            return p

        if shared.opts.cc_metadata and shared.opts.cc_metadata is True:
            cc_params = f'Alt: {latent}, Skip: {early}, Brightness: {bri}, Contrast: {con}, Saturation: {sat}, RGB: ({r}, {g}, {b}), Noise: {method}, Proc. Hr.F: {doHR}'
            p.extra_generation_params.update({f'Vec. CC [{VERSION}]': cc_params})

        bri /= steps
        con = pow(con, 1.0 / steps) - 1
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

            source = d[mode]

            # "Straight", "Straight Abs.", "Cross", "Cross Abs.", "Ones", "N.Random", "U.Random", "Multi-Res", "Multi-Res Abs."
            if 'Straight' in method:
                target = d[mode]
            elif 'Cross' in method: 
                cross = 'x' if mode == 'denoised' else 'denoised'
                target = d[cross]
            elif 'Multi-Res' in method:
                target = multires_noise(d[mode], 'Abs' in method)
            elif method == 'Ones':
                target = ones(d[mode])
            elif method == 'N.Random':
                target = normal_noise(d[mode])
            elif method ==  'U.Random':
                target = gaussian_noise(d[mode])

            if 'Abs' in method:
                target = to_abs(target)

            batchSize = d[mode].size(0)

            for i in range(batchSize):
                BRIGHTNESS = [source[i, 0], target[i, 0]]
                R = [source[i, 2], target[i, 2]]
                G = [source[i, 1], target[i, 1]]
                B = [source[i, 3], target[i, 3]]

                BRIGHTNESS[0] += BRIGHTNESS[1] * bri
                BRIGHTNESS[0] += BRIGHTNESS[1] * con

                R[0] -= R[1] * r
                G[0] += G[1] * g
                B[0] -= B[1] * b

                R[0] *= sat
                G[0] *= sat
                B[0] *= sat

            return og_callback(self, d)

        KDiffusionSampler.callback_state = callback_state
        return p

    def postprocess_image(self, p, *args):
        if hasattr(p, 'hr_pass'):
            del p.hr_pass

    def postprocess(self, p, processed, *args):
        KDiffusionSampler.callback_state = og_callback
