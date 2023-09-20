from modules.sd_samplers_kdiffusion import KDiffusionSampler
import modules.scripts as scripts
from modules import shared
import gradio as gr
import random

from scripts.cc_noise import *

from scripts.cc_xyz import xyz_support

from scripts.cc_scaling import apply_scaling

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
        clean_outdated('cc_hdr.py')

        self.xyzCache = {}
        xyz_support(self.xyzCache)

    def title(self):
        return "Vectorscope CC"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):

        with gr.Accordion(f"Vectorscope CC {VERSION}", elem_id='vec-cc-' + ('img' if is_img2img else 'txt'), open=False):

            with gr.Row():
                enable = gr.Checkbox(label="Enable")
                latent = gr.Checkbox(label="Alt.")
                early = gr.Slider(label="Skip", minimum=0.0, maximum=1.0, step=0.1, value=0.0)

            with gr.Row():
                bri = gr.Slider(label="Brightness", minimum=-6.0, maximum=6.0, step=0.1, value=0.0)
                con = gr.Slider(label="Contrast", minimum=-2.5, maximum=2.5, step=0.05, value=0.0)
                sat = gr.Slider(label="Saturation", minimum=0.25, maximum=1.75, step=0.05, value=1.0)

            with gr.Row():
                with gr.Column():
                    r = gr.Slider(label="R", info='Cyan | Red', minimum=-3.0, maximum=3.0, step=0.05, value=0.0, elem_id='cc-r-' + ('img' if is_img2img else 'txt'))
                    g = gr.Slider(label="G", info='Magenta | Green',minimum=-3.0, maximum=3.0, step=0.05, value=0.0, elem_id='cc-g-' + ('img' if is_img2img else 'txt'))
                    b = gr.Slider(label="B", info='Yellow | Blue',minimum=-3.0, maximum=3.0, step=0.05, value=0.0, elem_id='cc-b-' + ('img' if is_img2img else 'txt'))

                create_colorpicker(is_img2img)

                for component in [r, g, b]:
                    component.change(None, inputs=[r, g, b], outputs=[], _js=horizontal_js(is_img2img))
                    component.change(None, inputs=[r, g, b], outputs=[], _js=vertical_js(is_img2img))

            with gr.Accordion("Styles", open=False):

                with gr.Row():
                    style_choice = gr.Dropdown(label="Styles", choices=style_manager.list_style(), scale = 3)
                    apply_btn = gr.Button(value="Apply Style", elem_id='cc-apply-' + ('img' if is_img2img else 'txt'), scale = 2)
                    refresh_btn = gr.Button(value="Refresh Style", scale = 2)
                with gr.Row():
                    style_name = gr.Textbox(label="Style Name", scale = 3)
                    save_btn = gr.Button(value="Save Style", elem_id='cc-save-' + ('img' if is_img2img else 'txt'), scale = 2)
                    delete_btn = gr.Button(value="Delete Style", scale = 2)

                apply_btn.click(fn=style_manager.get_style, inputs=style_choice, outputs=[latent, bri, con, sat, r, g, b])
                save_btn.click(fn=lambda *args: gr.update(choices=style_manager.save_style(*args)), inputs=[style_name, latent, bri, con, sat, r, g, b], outputs=style_choice)
                delete_btn.click(fn=lambda name: gr.update(choices=style_manager.delete_style(name)), inputs=style_name, outputs=style_choice)
                refresh_btn.click(fn=lambda _: gr.update(choices=style_manager.list_style()), outputs=style_choice)

            with gr.Accordion("Advanced Settings", open=False):
                doHR = gr.Checkbox(label="Process Hires. fix")
                method = gr.Radio(["Straight", "Straight Abs.", "Cross", "Cross Abs.", "Ones", "N.Random", "U.Random", "Multi-Res", "Multi-Res Abs."], label="Noise Settings", value="Straight Abs.")
                scaling = gr.Radio(["Flat", "Cos", "Sin", "1 - Cos", "1 - Sin"], label="Scaling Settings", value="Flat")

            with gr.Row():
                reset_btn = gr.Button(value="Reset")
                self.register_reset(reset_btn, enable, latent, bri, con, sat, early, r, g, b, doHR, method, scaling)

                random_btn = gr.Button(value="Randomize")
                self.register_random(random_btn, bri, con, sat, r, g, b)

        self.infotext_fields = []
        self.paste_field_names = []
        self.infotext_fields = [
            (enable, lambda d: enable.update(value=("Vec CC Enabled" in d))),
            (latent, "Vec CC Alt"),
            (early, "Vec CC Skip"),
            (bri, "Vec CC Brightness"),
            (con, "Vec CC Contrast"),
            (sat, "Vec CC Saturation"),
            (r, "Vec CC R"),
            (g, "Vec CC G"),
            (b, "Vec CC B"),
            (method, "Vec CC Noise"),
            (doHR, "Vec CC Proc HrF"),
            (scaling, "Vec CC Scaling"),
        ]

        for _, name in self.infotext_fields:
            self.paste_field_names.append(name)

        return [enable, latent, bri, con, sat, early, r, g, b, doHR, method, scaling]

    def register_reset(self, reset_btn, enable, latent, bri, con, sat, early, r, g, b, doHR, method, scaling):
        for component in [enable, latent, doHR]:
            reset_btn.click(fn=lambda _: gr.update(value=False), outputs=component)
        for component in [early, bri, con, r, g, b]:
            reset_btn.click(fn=lambda _: gr.update(value=0.0), outputs=component)
        for component in [sat]:
            reset_btn.click(fn=lambda _: gr.update(value=1.0), outputs=component)

        reset_btn.click(fn=lambda _: gr.update(value='Straight Abs.'), outputs=method)
        reset_btn.click(fn=lambda _: gr.update(value='Flat'), outputs=scaling)

    def register_random(self, random_btn, bri, con, sat, r, g, b):
        for component in [bri, con, r, g, b]:
            random_btn.click(fn=lambda _: gr.update(value=round(random.uniform(-2.5, 2.5), 2)), outputs=component)
        for component in [sat]:
            random_btn.click(fn=lambda _: gr.update(value=round(random.uniform(0.5, 1.5), 2)), outputs=component)

    def parse_bool(self, string:str):
        if string.lower() == "true":
            return True
        if string.lower() == "false":
            return False

        raise ValueError(f"Invalid Value: {string}")

    def process(self, p, enable:bool, latent:bool, bri:float, con:float, sat:float, early:float, r:float, g:float, b:float, doHR:bool, method:str, scaling:str):
        if 'Enable' in self.xyzCache.keys():
            enable = self.parse_bool(self.xyzCache['Enable'])

        if not enable:
            if 'Enable' not in self.xyzCache.keys():
                if len(self.xyzCache) > 0:
                    print('\n[X/Y/Z Plot] x [Vec.CC] Extension is not Enabled!\n')
                self.xyzCache.clear()

            KDiffusionSampler.callback_state = og_callback
            return p

        if 'Random' in self.xyzCache.keys():
            if len(self.xyzCache) > 1:
                print('\n[X/Y/Z Plot] x [Vec.CC] Randomize is Enabled!\nSome settings will not apply!\n')
            else:
                print('\n[X/Y/Z Plot] x [Vec.CC] Randomize is Enabled!\n')

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
                case 'Scaling':
                    scaling = v
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

            bri = round(random.uniform(-3.0, 3.0), 2)
            r = round(random.uniform(-3.0, 3.0), 2)
            g = round(random.uniform(-3.0, 3.0), 2)
            b = round(random.uniform(-3.0, 3.0), 2)

            con = round(random.uniform(0.25, 1.75), 2)
            sat = round(random.uniform(0.25, 1.75), 2)

            print(f'-> Seed: {cc_seed}')
            print(f'Brightness:\t{bri}')
            print(f'Contrast:\t{con}')
            print(f'Saturation:\t{sat}')
            print(f'R:\t\t{r}')
            print(f'G:\t\t{g}')
            print(f'B:\t\t{b}\n')

        if stop < 1:
            return p

        if hasattr(shared.opts, 'cc_metadata') and shared.opts.cc_metadata is True:
            p.extra_generation_params['Vec CC Enabled'] = enable
            p.extra_generation_params['Vec CC Alt'] = latent
            p.extra_generation_params['Vec CC Skip'] = early
            p.extra_generation_params['Vec CC Brightness'] = bri
            p.extra_generation_params['Vec CC Contrast'] = con
            p.extra_generation_params['Vec CC Saturation'] = sat
            p.extra_generation_params['Vec CC R'] = r
            p.extra_generation_params['Vec CC G'] = g
            p.extra_generation_params['Vec CC B'] = b
            p.extra_generation_params['Vec CC Noise'] = method
            p.extra_generation_params['Vec CC Proc HrF'] = doHR
            p.extra_generation_params['Vec CC Scaling'] = scaling
            p.extra_generation_params['Vec CC Version'] = VERSION

        bri /= steps
        con /= steps
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

            mods = apply_scaling(scaling, d["i"], steps, bri, con, sat, r, g, b)

            for i in range(batchSize):
                BRIGHTNESS = [source[i, 0], target[i, 0]]
                R = [source[i, 2], target[i, 2]]
                G = [source[i, 1], target[i, 1]]
                B = [source[i, 3], target[i, 3]]

                BRIGHTNESS[0] += BRIGHTNESS[1] * mods[0]
                BRIGHTNESS[0] += get_delta(BRIGHTNESS[0]) * mods[1]

                R[0] -= R[1] * mods[3]
                G[0] += G[1] * mods[4]
                B[0] -= B[1] * mods[5]

                R[0] *= mods[2]
                G[0] *= mods[2]
                B[0] *= mods[2]

            return og_callback(self, d)

        KDiffusionSampler.callback_state = callback_state
        return p

    def postprocess_image(self, p, *args):
        if hasattr(p, 'hr_pass'):
            del p.hr_pass

    def postprocess(self, p, processed, *args):
        KDiffusionSampler.callback_state = og_callback
