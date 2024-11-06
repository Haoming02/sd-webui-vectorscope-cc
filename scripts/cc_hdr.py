from modules.processing import process_images, get_fixed_seed
from modules.shared import state
from modules import scripts
from copy import copy
import gradio as gr
import numpy as np
import cv2 as cv


def mergeHDR(imgs: list, path: str, depth: str, fmt: str, gamma: float):
    """https://docs.opencv.org/4.8.0/d2/df0/tutorial_py_hdr.html"""

    import datetime
    import math
    import os

    out_dir = os.path.join(os.path.dirname(path), "hdr")
    os.makedirs(out_dir, exist_ok=True)
    print(f'\nSaving HDR Outputs to "{out_dir}"\n')

    imgs_np = [np.asarray(img, dtype=np.uint8) for img in imgs]

    merge = cv.createMergeMertens()
    hdr = merge.process(imgs_np)

    # shift min to 0.0
    hdr += math.ceil(0.0 - np.min(hdr) * 1000) / 1000
    # print(f"({np.min(hdr)}, {np.max(hdr)}")

    target = 65535 if depth == "16bpc" else 255
    precision = np.uint16 if depth == "16bpc" else np.uint8

    hdr = np.power(hdr, (1 / gamma))

    ldr = np.clip(hdr * target, 0, target).astype(precision)
    rgb = cv.cvtColor(ldr, cv.COLOR_BGR2RGB)

    time = datetime.datetime.now().strftime("%H-%M-%S")
    cv.imwrite(os.path.join(out_dir, f"{time}{fmt}"), rgb)


class VectorHDR(scripts.Script):

    def title(self):
        return "High Dynamic Range"

    def show(self, is_img2img):
        return True

    def ui(self, is_img2img):

        with gr.Row():
            count = gr.Slider(
                label="Brackets",
                minimum=3,
                maximum=9,
                step=2,
                value=5,
            )

            gap = gr.Slider(
                label="Gaps",
                minimum=0.50,
                maximum=2.50,
                step=0.25,
                value=1.25,
            )

        with gr.Accordion(
            "Merge Options",
            elem_id=f'vec-hdr-{"img" if is_img2img else "txt"}',
            open=False,
        ):

            auto = gr.Checkbox(label="Automatically Merge", value=True)

            with gr.Row():
                depth = gr.Radio(["16bpc", "8bpc"], label="Bit Depth", value="16bpc")
                fmt = gr.Radio([".tiff", ".png"], label="Image Format", value=".tiff")

            gamma = gr.Slider(
                label="Gamma",
                info="Lower: Darker | Higher: Brighter",
                minimum=0.2,
                maximum=2.2,
                step=0.2,
                value=1.2,
            )

        for comp in (count, gap, auto, depth, fmt, gamma):
            comp.do_not_save_to_config = True

        return [count, gap, auto, depth, fmt, gamma]

    def run(
        self, p, count: int, gap: float, auto: bool, depth: str, fmt: str, gamma: float
    ):
        center: int = count // 2
        brackets = brightness_brackets(count, gap)

        p.seed = get_fixed_seed(p.seed)
        p.scripts.script("vectorscope cc").xyzCache.update({"Enable": "False"})

        baseline = process_images(p)
        pc = copy(p)

        imgs = [None] * count
        imgs[center] = baseline.images[0]

        for it in range(count):

            if state.skipped or state.interrupted or state.stopping_generation:
                print("HDR Process Skipped...")
                return baseline

            if it == center:
                continue

            pc.scripts.script("vectorscope cc").xyzCache.update(
                {
                    "Enable": "True",
                    "Alt": "True",
                    "Brightness": brackets[it],
                    "DoHR": "False",
                    "Method": "Ones",
                    "Scaling": "1 - Cos",
                }
            )

            proc = process_images(pc)
            imgs[it] = proc.images[0]

        if auto:
            mergeHDR(imgs, p.outpath_samples, depth, fmt, gamma)

        baseline.images = imgs
        return baseline


def brightness_brackets(count: int, gap: float) -> list[float]:
    half = count // 2
    return [gap * (i - half) for i in range(count)]
