from modules import scripts
import gradio as gr
import os

WHEEL = os.path.join(scripts.basedir(), "scripts", "vectorscope.png")
DOT = os.path.join(scripts.basedir(), "scripts", "dot.png")


def create_colorpicker(is_img: bool):
    m: str = "img" if is_img else "txt"

    whl = gr.Image(
        value=WHEEL,
        interactive=False,
        container=False,
        elem_id=f"cc-colorwheel-{m}",
    )

    dot = gr.Image(
        value=DOT,
        interactive=False,
        container=False,
        elem_id=f"cc-temp-{m}",
    )

    whl.do_not_save_to_config = True
    dot.do_not_save_to_config = True
