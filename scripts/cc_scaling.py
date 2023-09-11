from math import cos
from math import sin
from math import pi

def apply_scaling(alg:str, current_step:int, total_steps:int, bri:float, con:float, sat:float, r:float, g:float, b:float):
    ratio = float(current_step / total_steps)
    rad = ratio * pi / 2

    mod = 1.0

    match alg:
        case "Cos":
            mod = cos(rad)
        case "Sin":
            mod = sin(rad)
        case "1 - Cos":
            mod = (1 - cos(rad))
        case "1 - Sin":
            mod = (1 - sin(rad))

    return [
        bri * mod,
        con * mod,
        (sat - 1) * mod + 1,
        r * mod,
        g * mod,
        b * mod
    ]
