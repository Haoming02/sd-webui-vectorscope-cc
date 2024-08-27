from modules.sd_samplers_kdiffusion import KDiffusionSampler
from modules import shared, scripts

from lib_cc.colorpicker import create_colorpicker
from lib_cc.style import StyleManager
from lib_cc.xyz import xyz_support
from lib_cc import const

from random import seed
import gradio as gr
import lib_cc


VERSION = "v2.2.3"


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
        mode = "img" if is_img2img else "txt"
        m = f'"{mode}"'

        with gr.Accordion(
            f"Vectorscope CC {VERSION}", elem_id=f"vec-cc-{mode}", open=False
        ):

            with gr.Row():
                enable = gr.Checkbox(label="Enable")
                latent = gr.Checkbox(label="Alt. (Stronger Effects)")

            with gr.Row():
                bri = gr.Slider(
                    label="Brightness",
                    minimum=const.Brightness.minimum,
                    maximum=const.Brightness.maximum,
                    step=0.05,
                    value=const.Brightness.default,
                )
                con = gr.Slider(
                    label="Contrast",
                    minimum=const.Contrast.minimum,
                    maximum=const.Contrast.maximum,
                    step=0.05,
                    value=const.Contrast.default,
                )
                sat = gr.Slider(
                    label="Saturation",
                    minimum=const.Saturation.minimum,
                    maximum=const.Saturation.maximum,
                    step=0.05,
                    value=const.Saturation.default,
                )

            with gr.Row():
                with gr.Column():
                    r = gr.Slider(
                        label="R",
                        info="Cyan | Red",
                        minimum=const.Color.minimum,
                        maximum=const.Color.maximum,
                        step=0.05,
                        value=const.Color.default,
                        elem_id=f"cc-r-{mode}",
                    )
                    g = gr.Slider(
                        label="G",
                        info="Magenta | Green",
                        minimum=const.Color.minimum,
                        maximum=const.Color.maximum,
                        step=0.05,
                        value=const.Color.default,
                        elem_id=f"cc-g-{mode}",
                    )
                    b = gr.Slider(
                        label="B",
                        info="Yellow | Blue",
                        minimum=const.Color.minimum,
                        maximum=const.Color.maximum,
                        step=0.05,
                        value=const.Color.default,
                        elem_id=f"cc-b-{mode}",
                    )

                r.input(
                    None,
                    inputs=[r, g, b],
                    _js=f"(r, g, b) => {{ VectorscopeCC.updateCursor(r, g, b, {m}); }}",
                )
                g.input(
                    None,
                    inputs=[r, g, b],
                    _js=f"(r, g, b) => {{ VectorscopeCC.updateCursor(r, g, b, {m}); }}",
                )
                b.input(
                    None,
                    inputs=[r, g, b],
                    _js=f"(r, g, b) => {{ VectorscopeCC.updateCursor(r, g, b, {m}); }}",
                )

                create_colorpicker(is_img2img)

            with gr.Accordion("Styles", open=False):

                with gr.Row(elem_classes="style-rows"):
                    style_choice = gr.Dropdown(
                        label="Styles", choices=style_manager.list_style(), scale=3
                    )
                    apply_btn = gr.Button(
                        value="Apply Style", elem_id=f"cc-apply-{mode}", scale=2
                    )
                    refresh_btn = gr.Button(value="Refresh Style", scale=2)

                with gr.Row(elem_classes="style-rows"):
                    style_name = gr.Textbox(label="Style Name", scale=3)
                    save_btn = gr.Button(
                        value="Save Style", elem_id=f"cc-save-{mode}", scale=2
                    )
                    delete_btn = gr.Button(value="Delete Style", scale=2)

            with gr.Accordion("Advanced Settings", open=False):
                with gr.Row():
                    doHR = gr.Checkbox(label="Process Hires. fix")
                    doAD = gr.Checkbox(label="Process Adetailer")
                    doRN = gr.Checkbox(label="Randomize using Seed")

                method = gr.Radio(
                    [
                        "Straight",
                        "Straight Abs.",
                        "Cross",
                        "Cross Abs.",
                        "Ones",
                        "N.Random",
                        "U.Random",
                        "Multi-Res",
                        "Multi-Res Abs.",
                    ],
                    label="Noise Settings",
                    value="Straight Abs.",
                )
                scaling = gr.Radio(
                    ["Flat", "Cos", "Sin", "1 - Cos", "1 - Sin"],
                    label="Scaling Settings",
                    value="Flat",
                )

            comps = (
                latent,
                bri,
                con,
                sat,
                r,
                g,
                b,
                doHR,
                doAD,
                doRN,
                method,
                scaling,
            )

            apply_btn.click(
                fn=style_manager.get_style,
                inputs=style_choice,
                outputs=[*comps],
            ).then(
                None,
                inputs=[r, g, b],
                _js=f"(r, g, b) => {{ VectorscopeCC.updateCursor(r, g, b, {m}); }}",
            )

            save_btn.click(
                fn=lambda *args: gr.update(choices=style_manager.save_style(*args)),
                inputs=[style_name, *comps],
                outputs=style_choice,
            )

            delete_btn.click(
                fn=lambda name: gr.update(choices=style_manager.delete_style(name)),
                inputs=style_name,
                outputs=style_choice,
            )

            refresh_btn.click(
                fn=lambda _: gr.update(choices=style_manager.load_styles()),
                outputs=style_choice,
            )

            with gr.Row():
                reset_btn = gr.Button(value="Reset")
                random_btn = gr.Button(value="Randomize")

                def on_reset():
                    return [
                        gr.update(value=False),
                        gr.update(value=const.Brightness.default),
                        gr.update(value=const.Contrast.default),
                        gr.update(value=const.Saturation.default),
                        gr.update(value=const.Color.default),
                        gr.update(value=const.Color.default),
                        gr.update(value=const.Color.default),
                        gr.update(value=False),
                        gr.update(value=False),
                        gr.update(value=False),
                        gr.update(value="Straight Abs."),
                        gr.update(value="Flat"),
                    ]

                def on_random():
                    return [
                        gr.update(value=const.Brightness.rand()),
                        gr.update(value=const.Contrast.rand()),
                        gr.update(value=const.Saturation.rand()),
                        gr.update(value=const.Color.rand()),
                        gr.update(value=const.Color.rand()),
                        gr.update(value=const.Color.rand()),
                    ]

                reset_btn.click(
                    fn=on_reset,
                    outputs=[*comps],
                    show_progress="hidden",
                ).then(
                    None,
                    inputs=[r, g, b],
                    _js=f"(r, g, b) => {{ VectorscopeCC.updateCursor(r, g, b, {m}); }}",
                )

                random_btn.click(
                    fn=on_random,
                    outputs=[bri, con, sat, r, g, b],
                    show_progress="hidden",
                ).then(
                    None,
                    inputs=[r, g, b],
                    _js=f"(r, g, b) => {{ VectorscopeCC.updateCursor(r, g, b, {m}); }}",
                )

        self.paste_field_names = []
        self.infotext_fields = [
            (enable, "Vec CC Enabled"),
            (latent, "Vec CC Alt"),
            (bri, "Vec CC Brightness"),
            (con, "Vec CC Contrast"),
            (sat, "Vec CC Saturation"),
            (r, "Vec CC R"),
            (g, "Vec CC G"),
            (b, "Vec CC B"),
            (method, "Vec CC Noise"),
            (doHR, "Vec CC Proc HrF"),
            (doAD, "Vec CC Proc Ade"),
            (doRN, "Vec CC Seed Randomize"),
            (scaling, "Vec CC Scaling"),
        ]

        for comp, name in self.infotext_fields:
            comp.do_not_save_to_config = True
            self.paste_field_names.append(name)

        return [enable, *comps]

    def process_batch(
        self,
        p,
        enable: bool,
        latent: bool,
        bri: float,
        con: float,
        sat: float,
        r: float,
        g: float,
        b: float,
        doHR: bool,
        doAD: bool,
        doRN: bool,
        method: str,
        scaling: str,
        batch_number: int,
        prompts: list[str],
        seeds: list[int],
        subseeds: list[int],
    ):
        if "Enable" in self.xyzCache.keys():
            enable = self.xyzCache["Enable"].lower().strip() == "true"

        if not enable:
            if "Enable" not in self.xyzCache.keys():
                if len(self.xyzCache) > 0:
                    print("\n[Vec.CC] x [X/Y/Z Plot] Extension is not Enabled!\n")

                self.xyzCache.clear()

            KDiffusionSampler.vec_cc = {"enable": False}
            return p

        if "Random" in self.xyzCache.keys():
            if len(self.xyzCache) > 1:
                print(
                    "\n[X/Y/Z Plot] x [Vec.CC] Randomize is Enabled.\nSome settings will not apply!\n"
                )
            else:
                print("\n[X/Y/Z Plot] x [Vec.CC] Randomize is Enabled.\n")

        cc_seed = int(seeds[0]) if doRN else None

        for k, v in self.xyzCache.items():
            match k:
                case "Alt":
                    latent = self.xyzCache["Alt"].lower().strip() == "true"
                case "Brightness":
                    bri = float(v)
                case "Contrast":
                    con = float(v)
                case "Saturation":
                    sat = float(v)
                case "R":
                    r = float(v)
                case "G":
                    g = float(v)
                case "B":
                    b = float(v)
                case "DoHR":
                    doHR = self.xyzCache["DoHR"].lower().strip() == "true"
                case "Method":
                    method = str(v)
                case "Scaling":
                    scaling = str(v)
                case "Random":
                    cc_seed = int(v)

        self.xyzCache.clear()

        if method == "Disabled":
            KDiffusionSampler.vec_cc = {"enable": False}
            return p

        steps: int = p.steps
        # is img2img & do full steps
        if not hasattr(p, "enable_hr") and not shared.opts.img2img_fix_steps:
            if getattr(p, "denoising_strength", 1.0) < 1.0:
                steps = int(steps * getattr(p, "denoising_strength", 1.0) + 1.0)

        if cc_seed:
            seed(cc_seed)

            bri = const.Brightness.rand()
            con = const.Contrast.rand()
            sat = const.Saturation.rand()

            r = const.Color.rand()
            g = const.Color.rand()
            b = const.Color.rand()

            print(f"\n-> Seed: {cc_seed}")
            print(f"Brightness:\t{bri}")
            print(f"Contrast:\t{con}")
            print(f"Saturation:\t{sat}")
            print(f"R:\t\t{r}")
            print(f"G:\t\t{g}")
            print(f"B:\t\t{b}\n")

        if getattr(shared.opts, "cc_metadata", True):
            p.extra_generation_params["Vec CC Enabled"] = enable
            p.extra_generation_params["Vec CC Alt"] = latent
            p.extra_generation_params["Vec CC Brightness"] = bri
            p.extra_generation_params["Vec CC Contrast"] = con
            p.extra_generation_params["Vec CC Saturation"] = sat
            p.extra_generation_params["Vec CC R"] = r
            p.extra_generation_params["Vec CC G"] = g
            p.extra_generation_params["Vec CC B"] = b
            p.extra_generation_params["Vec CC Noise"] = method
            p.extra_generation_params["Vec CC Proc HrF"] = doHR
            p.extra_generation_params["Vec CC Proc Ade"] = doAD
            p.extra_generation_params["Vec CC Scaling"] = scaling
            p.extra_generation_params["Vec CC Version"] = VERSION

        bri /= steps
        con /= steps
        sat = pow(sat, 1.0 / steps)
        r /= steps
        g /= steps
        b /= steps

        mode = "x" if latent else "denoised"

        KDiffusionSampler.vec_cc = {
            "enable": True,
            "mode": mode,
            "bri": bri,
            "con": con,
            "sat": sat,
            "r": r,
            "g": g,
            "b": b,
            "method": method,
            "doHR": doHR,
            "doAD": doAD,
            "scaling": scaling,
            "step": steps,
        }

        return p
