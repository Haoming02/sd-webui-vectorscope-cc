from modules import scripts
import gradio as gr
import os

WHEEL = os.path.join(scripts.basedir(), "scripts", "Vectorscope.png")
DOT = os.path.join(scripts.basedir(), "scripts", "dot.png")


def create_colorpicker(is_img: bool):
    m: str = "img" if is_img else "txt"

    gr.Image(
        value=WHEEL,
        interactive=False,
        container=False,
        elem_id=f"cc-colorwheel-{m}",
    )

    gr.Image(
        value=DOT,
        interactive=False,
        container=False,
        elem_id=f"cc-temp-{m}",
    )
