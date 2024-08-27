from modules import scripts
import gradio as gr
import os

WHEEL = os.path.join(scripts.basedir(), "scripts", "Vectorscope.png")
DOT = os.path.join(scripts.basedir(), "scripts", "dot.png")


def create_colorpicker(is_img: bool):
    m = "img" if is_img else "txt"

    gr.Image(
        WHEEL,
        interactive=False,
        container=False,
        elem_id=f"cc-colorwheel-{m}",
    )

    gr.Image(
        DOT,
        interactive=False,
        container=False,
        elem_id=f"cc-temp-{m}",
    )
