from modules.processing import process_images, get_fixed_seed
from modules import scripts
from copy import copy
import gradio as gr
import numpy as np
import cv2 as cv


# https://docs.opencv.org/4.8.0/d2/df0/tutorial_py_hdr.html
def merge_HDR(imgs: list, path: str, depth: str, fmt: str, gamma: float):
    import datetime
    import math
    import os

    output_folder = os.path.join(path, "hdr")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    imgs_np = [np.array(img, dtype=np.uint8) for img in imgs]

    merge = cv.createMergeMertens()
    hdr = merge.process(imgs_np)
    hdr += math.ceil(0 - np.min(hdr) * 1000) / 1000

    # print(f'{np.min(hdr)}, {np.max(hdr)}')

    target = 65535 if depth == "16bpc" else 255
    precision = "uint16" if depth == "16bpc" else "uint8"

    hdr = np.power(hdr, (1 / gamma))

    ldr = np.clip(hdr * target, 0, target).astype(precision)
    rgb = cv.cvtColor(ldr, cv.COLOR_BGR2RGB)

    cv.imwrite(
        os.path.join(
            output_folder, f'{datetime.datetime.now().strftime("%H-%M-%S")}{fmt}'
        ),
        rgb,
    )


class VectorHDR(scripts.Script):
    def title(self):
        return "High Dynamic Range"

    def show(self, is_img2img):
        return True

    def ui(self, is_img2img):
        with gr.Row():
            count = gr.Slider(label="Brackets", minimum=3, maximum=9, step=2, value=7)
            gap = gr.Slider(
                label="Gaps", minimum=0.50, maximum=2.50, step=0.25, value=1.50
            )

        with gr.Accordion(
            "Merge Options",
            elem_id="vec-hdr-" + ("img" if is_img2img else "txt"),
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

        for comp in [count, gap, auto, depth, fmt, gamma]:
            comp.do_not_save_to_config = True

        return [count, gap, auto, depth, fmt, gamma]

    def run(
        self, p, count: int, gap: float, auto: bool, depth: str, fmt: str, gamma: float
    ):
        center = count // 2

        p.seed = get_fixed_seed(p.seed)
        p.scripts.script("vectorscope cc").xyzCache.update(
            {
                "Enable": "True",
                "Alt": "True",
                "Brightness": 0,
                "DoHR": "False",
                "Method": "Ones",
                "Scaling": "1 - Cos",
            }
        )

        baseline = process_images(p)
        pc = copy(p)

        imgs = [None] * count
        imgs[center] = baseline.images[0]

        brackets = brightness_brackets(count, gap)

        for it in range(count):
            if it == center:
                continue

            pc.scripts.script("vectorscope cc").xyzCache.update(
                {"Brightness": brackets[it]}
            )

            proc = process_images(pc)
            imgs[it] = proc.images[0]

        if not auto:
            baseline.images = imgs
            return baseline

        else:
            merge_HDR(imgs, p.outpath_samples, depth, fmt, gamma)
            return baseline


def brightness_brackets(count, gap):
    half = count // 2
    return [gap * (i - half) for i in range(count)]
