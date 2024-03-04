import modules.scripts as scripts
import gradio as gr
import os

WHEEL = os.path.join(scripts.basedir(), "scripts", "Vectorscope.png")
DOT = os.path.join(scripts.basedir(), "scripts", "dot.png")


def create_colorpicker(is_img: bool):

    gr.Image(
        WHEEL,
        interactive=False,
        container=False,
        elem_id=f"cc-colorwheel-{'img' if is_img else 'txt'}",
    )

    gr.Image(
        DOT,
        interactive=False,
        container=False,
        elem_id=f"cc-temp-{'img' if is_img else 'txt'}",
    )
