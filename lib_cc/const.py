import random


class Param:

    def __init__(self, minimum: float, maximum: float, default: float):
        self.minimum = minimum
        self.maximum = maximum
        self.default = default

    def rand(self) -> float:
        return round(random.uniform(self.minimum, self.maximum), 2)


Brightness = Param(-5.0, 5.0, 0.0)
Contrast = Param(-5.0, 5.0, 0.0)
Saturation = Param(0.25, 1.75, 1.0)
Color = Param(-4.0, 4.0, 0.0)
