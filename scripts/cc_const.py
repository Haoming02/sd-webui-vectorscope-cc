class Param:
    def __init__(self, minimum: float, maximum: float, default: float):
        self.minimum = minimum
        self.maximum = maximum
        self.default = default

Brightness = Param(-5.0, 5.0, 0.0)
Contrast = Param(-5.0, 5.0, 0.0)
Saturation = Param(0.25, 1.75, 1.0)
COLOR = Param(-4.0, 4.0, 0.0)
