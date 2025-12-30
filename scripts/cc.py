from modules.sd_samplers_kdiffusion import KDiffusionSampler
from modules.shared import opts
from modules import scripts

from lib_cc.const import rand_method, rand_scaling
from lib_cc.colorpicker import create_colorpicker
from lib_cc.callback import hook_callbacks
from lib_cc.style import StyleManager
from lib_cc.xyz import xyz_support
from lib_cc import const

from random import seed
import gradio as gr


VERSION = "2.4.0"


style_manager = StyleManager()
style_manager.load_styles()
hook_callbacks()
const.init()


class VectorscopeCC(scripts.Script):

    def __init__(self):
        self.xyzCache = {}
        xyz_support(self.xyzCache)

    def title(self):
        return "Vectorscope CC"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        mode: str = "img" if is_img2img else "txt"
        m: str = f'"{mode}"'

        with gr.Accordion(
            f"Vectorscope CC v{VERSION}", elem_id=f"vec-cc-{mode}", open=False
        ):

            with gr.Row():
                enable = gr.Checkbox(label="Enable")
                latent = gr.Checkbox(label="Alt. (Stronger Effects)")

            with gr.Row():
                bri = gr.Slider(
                    label="Brightness",
                    value=const.Brightness.default,
                    minimum=const.Brightness.minimum,
                    maximum=const.Brightness.maximum,
                    step=0.05,
                )
                con = gr.Slider(
                    label="Contrast",
                    value=const.Contrast.default,
                    minimum=const.Contrast.minimum,
                    maximum=const.Contrast.maximum,
                    step=0.05,
                )
                sat = gr.Slider(
                    label="Saturation",
                    value=const.Saturation.default,
                    minimum=const.Saturation.minimum,
                    maximum=const.Saturation.maximum,
                    step=0.05,
                )

            with gr.Row():
                with gr.Column():
                    r = gr.Slider(
                        label="R",
                        info="Cyan | Red",
                        value=const.Color.default,
                        minimum=const.Color.minimum,
                        maximum=const.Color.maximum,
                        step=0.05,
                        elem_id=f"cc-r-{mode}",
                    )
                    g = gr.Slider(
                        label="G",
                        info="Magenta | Green",
                        value=const.Color.default,
                        minimum=const.Color.minimum,
                        maximum=const.Color.maximum,
                        step=0.05,
                        elem_id=f"cc-g-{mode}",
                    )
                    b = gr.Slider(
                        label="B",
                        info="Yellow | Blue",
                        value=const.Color.default,
                        minimum=const.Color.minimum,
                        maximum=const.Color.maximum,
                        step=0.05,
                        elem_id=f"cc-b-{mode}",
                    )

                for c in (r, g, b):
                    c.input(
                        None,
                        inputs=[r, g, b],
                        _js=f"(r, g, b) => {{ VectorscopeCC.updateCursor(r, g, b, {m}); }}",
                    )

                create_colorpicker(is_img2img)

            with gr.Accordion("Styles", open=False):

                with gr.Row(elem_classes="style-rows"):
                    style_choice = gr.Dropdown(
                        label="CC Styles", choices=style_manager.list_style(), scale=3
                    )
                    apply_btn = gr.Button(
                        value="Apply Style", elem_id=f"cc-apply-{mode}", scale=2
                    )
                    refresh_btn = gr.Button(value="Refresh Style", scale=2)

                with gr.Row(elem_classes="style-rows"):
                    style_name = gr.Textbox(
                        label="Style Name", lines=1, max_lines=1, scale=3
                    )
                    save_btn = gr.Button(
                        value="Save Style", elem_id=f"cc-save-{mode}", scale=2
                    )
                    delete_btn = gr.Button(value="Delete Style", scale=2)

            if getattr(opts, "cc_no_defaults", True):
                style_choice.do_not_save_to_config = True

            [
                setattr(comp, "do_not_save_to_config", True)
                for comp in (
                    apply_btn,
                    refresh_btn,
                    style_name,
                    save_btn,
                    delete_btn,
                )
            ]

            with gr.Accordion("Advanced Settings", open=False):
                with gr.Row():
                    doHR = gr.Checkbox(
                        label="Process Hires. fix",
                        visible=(not is_img2img),
                    )
                    doAD = gr.Checkbox(label="Process Adetailer")
                    doRN = gr.Checkbox(label="Randomize using Seed")

                method = gr.Radio(
                    choices=(
                        "Straight",
                        "Straight Abs.",
                        "Cross",
                        "Cross Abs.",
                        "Ones",
                        "N.Random",
                        "U.Random",
                        "Multi-Res",
                        "Multi-Res Abs.",
                    ),
                    label="Noise Settings",
                    value="Straight Abs.",
                )

                scaling = gr.Radio(
                    choices=("Flat", "Cos", "Sin", "1 - Cos", "1 - Sin"),
                    label="Scaling Settings",
                    value="Flat",
                )

            comps: tuple[gr.components.Component] = (
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
                inputs=[style_choice],
                outputs=[*comps],
            ).then(
                None,
                inputs=[r, g, b],
                _js=f"(r, g, b) => {{ VectorscopeCC.updateCursor(r, g, b, {m}); }}",
            )

            save_btn.click(
                fn=lambda *args: gr.update(choices=style_manager.save_style(*args)),
                inputs=[style_name, *comps],
                outputs=[style_choice],
            )

            delete_btn.click(
                fn=lambda name: gr.update(choices=style_manager.delete_style(name)),
                inputs=[style_name],
                outputs=[style_choice],
            )

            refresh_btn.click(
                fn=lambda: gr.update(choices=style_manager.load_styles()),
                outputs=[style_choice],
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
                        rand_method(),
                        rand_scaling(),
                    ]

                reset_btn.click(
                    fn=on_reset,
                    outputs=[*comps],
                    show_progress="hidden",
                ).then(
                    fn=None,
                    inputs=[r, g, b],
                    _js=f"(r, g, b) => {{ VectorscopeCC.updateCursor(r, g, b, {m}); }}",
                )

                random_btn.click(
                    fn=on_random,
                    outputs=[bri, con, sat, r, g, b, method, scaling],
                    show_progress="hidden",
                ).then(
                    fn=None,
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
            if getattr(opts, "cc_no_defaults", True):
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

        enable = self.xyzCache.pop("Enable", str(enable)).lower().strip() == "true"

        if not enable:
            if len(self.xyzCache) > 0:
                print("\n[Vec.CC] x [X/Y/Z Plot] Extension is not Enabled!\n")
                self.xyzCache.clear()

            setattr(KDiffusionSampler, "vec_cc", {"enable": False})
            return p

        method = str(self.xyzCache.pop("Method", method))

        if method == "Disabled":
            setattr(KDiffusionSampler, "vec_cc", {"enable": False})
            return p

        if "Random" in self.xyzCache.keys():
            print("[X/Y/Z Plot] x [Vec.CC] Randomize is Enabled.")
            if len(self.xyzCache) > 1:
                print("Some parameters will be overridden!")

            cc_seed = int(self.xyzCache.pop("Random"))
        else:
            cc_seed = int(seeds[0]) if doRN else None

        latent = self.xyzCache.pop("Alt", str(latent)).lower().strip() == "true"
        doHR = self.xyzCache.pop("DoHR", str(doHR)).lower().strip() == "true"
        scaling = str(self.xyzCache.pop("Scaling", scaling))

        bri = float(self.xyzCache.pop("Brightness", bri))
        con = float(self.xyzCache.pop("Contrast", con))
        sat = float(self.xyzCache.pop("Saturation", sat))

        r = float(self.xyzCache.pop("R", r))
        g = float(self.xyzCache.pop("G", g))
        b = float(self.xyzCache.pop("B", b))

        assert len(self.xyzCache) == 0

        if cc_seed:
            seed(cc_seed)

            bri = const.Brightness.rand()
            con = const.Contrast.rand()
            sat = const.Saturation.rand()

            r = const.Color.rand()
            g = const.Color.rand()
            b = const.Color.rand()

            print(f"\n\n[Seed: {cc_seed}]")
            print(f"> Brightness:   {bri}")
            print(f"> Contrast:     {con}")
            print(f"> Saturation:   {sat}")
            print(f"> R:            {r}")
            print(f"> G:            {g}")
            print(f"> B:            {b}")

            if getattr(opts, "cc_rand_method", False):
                method = rand_method(orig=method)
                print(f"> Noise:        {method}")

            if getattr(opts, "cc_rand_scaling", False):
                scaling = rand_method(orig=scaling)
                print(f"> Scaling:      {scaling}")

            print("\n")

        if getattr(opts, "cc_metadata", True):
            p.extra_generation_params.update(
                {
                    "Vec CC Enabled": enable,
                    "Vec CC Alt": latent,
                    "Vec CC Brightness": bri,
                    "Vec CC Contrast": con,
                    "Vec CC Saturation": sat,
                    "Vec CC R": r,
                    "Vec CC G": g,
                    "Vec CC B": b,
                    "Vec CC Noise": method,
                    "Vec CC Proc HrF": doHR,
                    "Vec CC Proc Ade": doAD,
                    "Vec CC Seed Randomize": doRN,
                    "Vec CC Scaling": scaling,
                    "Vec CC Version": VERSION,
                }
            )

        steps: int = getattr(p, "firstpass_steps", None) or p.steps

        bri /= steps
        con /= steps
        sat = pow(sat, 1.0 / steps)
        r /= steps
        g /= steps
        b /= steps

        mode: str = "x" if latent else "denoised"

        setattr(
            KDiffusionSampler,
            "vec_cc",
            {
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
            },
        )

        return p

    def before_hr(self, p, enable: bool, *args, **kwargs):

        if enable:
            steps: int = getattr(p, "hr_second_pass_steps", None) or p.steps
            KDiffusionSampler.vec_cc["step"] = steps

        return p
