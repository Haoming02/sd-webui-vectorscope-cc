from modules.shared import opts
import random


class Param:

    def __init__(self, minimum: float, maximum: float, default: float):
        self.minimum = minimum
        self.maximum = maximum
        self.default = default

    def rand(self) -> float:
        return round(random.uniform(self.minimum, self.maximum), 2)


Brightness: Param = None
Contrast: Param = None
Saturation: Param = None
Color: Param = None


def init():
    global Brightness
    Brightness = Param(
        getattr(opts, "cc_brightness_min", -5.0),
        getattr(opts, "cc_brightness_max", 5.0),
        0.0,
    )

    global Contrast
    Contrast = Param(
        getattr(opts, "cc_contrast_min", -5.0),
        getattr(opts, "cc_contrast_max", 5.0),
        0.0,
    )

    global Saturation
    Saturation = Param(
        getattr(opts, "cc_saturation_min", 0.25),
        getattr(opts, "cc_saturation_max", 1.75),
        1.0,
    )

    global Color
    Color = Param(
        getattr(opts, "cc_color_min", -4.0),
        getattr(opts, "cc_color_max", 4.0),
        0.0,
    )
