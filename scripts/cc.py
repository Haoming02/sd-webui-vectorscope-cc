from modules.sd_samplers_kdiffusion import KDiffusionSampler
import modules.scripts as scripts
from modules import shared
import gradio as gr
import torch

class VectorscopeCC(scripts.Script):
    def __init__(self):
        global og_callback
        og_callback = KDiffusionSampler.callback_state

    def title(self):
        return "Vectorscope Color Correction"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        with gr.Accordion("Vectorscope CC", open=False):

            with gr.Row() as basics:
                enable = gr.Checkbox(label="Enable")
                latent = gr.Checkbox(label="Alt.")

            with gr.Row() as BnC:
                bri = gr.Slider(label="Brightness", minimum=-5.0, maximum=5.0, step=0.05, value=0.0)
                con = gr.Slider(label="Contrast", minimum=-2.0, maximum=2.0, step=0.05, value=0.0)

            with gr.Row() as SS:
                sat = gr.Slider(label="Saturation", minimum=-2.0, maximum=2.0, step=0.05, value=0.0)
                early = gr.Slider(label="Skip", minimum=0.0, maximum=1.0, step=0.05, value=0.1)

            with gr.Row() as RGB:
                r = gr.Slider(label="R", info='Cyan | Red', minimum=-2.0, maximum=2.0, step=0.05, value=0.0)
                g = gr.Slider(label="G", info='Magenta | Green',minimum=-2.0, maximum=2.0, step=0.05, value=0.0)
                b = gr.Slider(label="B", info='Yellow | Blue',minimum=-2.0, maximum=2.0, step=0.05, value=0.0)

        return [enable, latent, bri, con, sat, early, r, g, b]

    def process(self, p, enable:bool, latent:bool, bri:float, con:float, sat:float, early:float, r:float, g:float, b:float):
        if not enable:
            setattr(KDiffusionSampler, "callback_state", og_callback)
            return p

        steps = p.steps
        if not hasattr(p, 'enable_hr') and hasattr(p, 'denoising_strength') and not shared.opts.img2img_fix_steps:
            steps = int(steps * p.denoising_strength)

        stop = int(steps * (1 - early))

        if stop < 1:
            return p

        bri /= steps
        con = 1.0 + con / steps
        sat = 1.0 + sat / steps
        r /= steps
        g /= steps
        b /= steps

        mode = 'x' if latent else 'denoised'

        # Channel 0:    Dark    |   Bright
        # Channel 1:    Purple  |   Green
        # Channel 2:    Red     |   Cyan
        # Channel 2:    Violet  |   Yellow

        def callback_state(self, d):
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

            BRIGHTNESS = d[mode][0, 0]
            R = d[mode][0, 2]
            G = d[mode][0, 1]
            B = d[mode][0, 3]

            BRIGHTNESS += torch.abs(BRIGHTNESS) * bri
            BRIGHTNESS *= con

            R -= r
            G += g
            B -= b

            R *= sat
            G *= sat
            B *= sat

            return og_callback(self, d)

        setattr(KDiffusionSampler, "callback_state", callback_state)
        return p

    def postprocess(self, p, processed, *args):
        setattr(KDiffusionSampler, "callback_state", og_callback)