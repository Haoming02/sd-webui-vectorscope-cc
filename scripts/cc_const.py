class Param():
    def __init__(self, minimum, maximum, default):
        self.minimum = minimum
        self.maximum = maximum
        self.default = default

Brightness = Param(-6.0, 6.0, 0.0)
Contrast = Param(-5.0, 5.0, 0.0)
Saturation = Param(0.2, 1.8, 1.0)
R = Param(-4.0, 4.0, 0.0)
G = Param(-4.0, 4.0, 0.0)
B = Param(-4.0, 4.0, 0.0)
