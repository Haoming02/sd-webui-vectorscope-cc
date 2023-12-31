from modules.sd_samplers_kdiffusion import KDiffusionSampler
import modules.scripts as scripts
import scripts.cc_const as const
from modules import shared
import gradio as gr
import random

from scripts.cc_xyz import xyz_support

from scripts.cc_version import VERSION

from scripts.cc_colorpicker import create_colorpicker
from scripts.cc_colorpicker import horizontal_js
from scripts.cc_colorpicker import vertical_js

from scripts.cc_style import StyleManager
style_manager = StyleManager()
style_manager.load_styles()

class VectorscopeCC(scripts.Script):
    def __init__(self):
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
                latent = gr.Checkbox(label="Alt. (Stronger Effects)")

            with gr.Row():
                bri = gr.Slider(label="Brightness", minimum=const.Brightness.minimum, maximum=const.Brightness.maximum, step=0.1, value=const.Brightness.default)
                con = gr.Slider(label="Contrast", minimum=const.Contrast.minimum, maximum=const.Contrast.maximum, step=0.05, value=const.Contrast.default)
                sat = gr.Slider(label="Saturation", minimum=const.Saturation.minimum, maximum=const.Saturation.maximum, step=0.05, value=const.Saturation.default)

            with gr.Row():
                with gr.Column():
                    r = gr.Slider(label="R", info='Cyan | Red', minimum=const.R.minimum, maximum=const.R.maximum, step=0.05, value=const.R.default, elem_id='cc-r-' + ('img' if is_img2img else 'txt'))
                    g = gr.Slider(label="G", info='Magenta | Green',minimum=const.G.minimum, maximum=const.G.maximum, step=0.05, value=const.G.default, elem_id='cc-g-' + ('img' if is_img2img else 'txt'))
                    b = gr.Slider(label="B", info='Yellow | Blue',minimum=const.B.minimum, maximum=const.B.maximum, step=0.05, value=const.B.default, elem_id='cc-b-' + ('img' if is_img2img else 'txt'))

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
                self.register_reset(reset_btn, latent, bri, con, sat, r, g, b, doHR, method, scaling)

                random_btn = gr.Button(value="Randomize")
                self.register_random(random_btn, bri, con, sat, r, g, b)

        self.paste_field_names = []
        self.infotext_fields = [
            (enable, lambda d: enable.update(value=("Vec CC Enabled" in d))),
            (latent, "Vec CC Alt"),
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

        return [enable, latent, bri, con, sat, r, g, b, doHR, method, scaling]

    def register_reset(self, reset_btn, latent, bri, con, sat, r, g, b, doHR, method, scaling):
        for component in [latent, doHR]:
            reset_btn.click(fn=lambda _: gr.update(value=False), outputs=component)
        for component in [bri, con, r, g, b]:
            reset_btn.click(fn=lambda _: gr.update(value=0.0), outputs=component)
        for component in [sat]:
            reset_btn.click(fn=lambda _: gr.update(value=const.Saturation.default), outputs=component)

        reset_btn.click(fn=lambda _: gr.update(value='Straight Abs.'), outputs=method)
        reset_btn.click(fn=lambda _: gr.update(value='Flat'), outputs=scaling)

    def register_random(self, random_btn, bri, con, sat, r, g, b):
        for component in [bri, con, r, g, b]:
            random_btn.click(fn=lambda _: gr.update(value=round(random.uniform(const.R.minimum, const.R.maximum), 2)), outputs=component)
        for component in [sat]:
            random_btn.click(fn=lambda _: gr.update(value=round(random.uniform(const.Saturation.minimum, const.Saturation.maximum), 2)), outputs=component)

    def parse_bool(self, string:str):
        if string.lower() == "true":
            return True
        if string.lower() == "false":
            return False

        raise ValueError(f"Invalid Value: {string}")

    def process(self, p, enable:bool, latent:bool, bri:float, con:float, sat:float, r:float, g:float, b:float, doHR:bool, method:str, scaling:str):
        KDiffusionSampler.isHR_Pass = False

        if 'Enable' in self.xyzCache.keys():
            enable = self.parse_bool(self.xyzCache['Enable'])

        if not enable:
            if 'Enable' not in self.xyzCache.keys():
                if len(self.xyzCache) > 0:
                    print('\n[X/Y/Z Plot] x [Vec.CC] Extension is not Enabled!\n')
                self.xyzCache.clear()

            KDiffusionSampler.vec_cc = {'enable': False}
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
            KDiffusionSampler.vec_cc = {'enable': False}
            return p

        steps = p.steps
        if not hasattr(p, 'enable_hr') and hasattr(p, 'denoising_strength') and not shared.opts.img2img_fix_steps:
            steps = int(steps * p.denoising_strength)

        if cc_seed is not None:
            random.seed(cc_seed)

            bri = round(random.uniform(const.Contrast.minimum, const.Contrast.maximum), 2)
            con = round(random.uniform(const.Contrast.minimum, const.Contrast.maximum), 2)
            r = round(random.uniform(const.R.minimum, const.R.maximum), 2)
            g = round(random.uniform(const.G.minimum, const.G.maximum), 2)
            b = round(random.uniform(const.B.minimum, const.B.maximum), 2)

            sat = round(random.uniform(const.Saturation.minimum, const.Saturation.maximum), 2)

            print(f'-> Seed: {cc_seed}')
            print(f'Brightness:\t{bri}')
            print(f'Contrast:\t{con}')
            print(f'Saturation:\t{sat}')
            print(f'R:\t\t{r}')
            print(f'G:\t\t{g}')
            print(f'B:\t\t{b}\n')

        if hasattr(shared.opts, 'cc_metadata') and shared.opts.cc_metadata is True:
            p.extra_generation_params['Vec CC Enabled'] = enable
            p.extra_generation_params['Vec CC Alt'] = latent
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

        KDiffusionSampler.vec_cc = {
            'enable': True,
            'mode' : mode,
            'bri': bri,
            'con': con,
            'sat': sat,
            'r': r,
            'g': g,
            'b': b,
            'method': method,
            'doHR': doHR,
            'scaling': scaling,
            'step': steps
        }

        return p

    def before_hr(self, p, *args):
        KDiffusionSampler.isHR_Pass = True
