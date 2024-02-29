from modules.sd_samplers_common import Sampler
from modules import script_callbacks
from scripts.cc_scaling import apply_scaling
from scripts.cc_noise import *

original_callback = Sampler.callback_state

def cc_callback(self, d):
    if not self.vec_cc['enable']:
        return original_callback(self, d)

    if not self.vec_cc['doHR'] and self.isHR_Pass is True:
        return original_callback(self, d)

    mode = self.vec_cc['mode']
    method = self.vec_cc['method']

    source = d[mode]

    # "Straight", "Straight Abs.", "Cross", "Cross Abs.", "Ones", "N.Random", "U.Random", "Multi-Res", "Multi-Res Abs."
    if 'Straight' in method:
        target = d[mode]
    elif 'Cross' in method:
        cross = 'x' if mode == 'denoised' else 'denoised'
        target = d[cross]
    elif 'Multi-Res' in method:
        target = multires_noise(d[mode], 'Abs' in method)
    elif method == 'Ones':
        target = ones(d[mode])
    elif method == 'N.Random':
        target = normal_noise(d[mode])
    elif method ==  'U.Random':
        target = gaussian_noise(d[mode])

    if 'Abs' in method:
        target = to_abs(target)

    batchSize = d[mode].size(0)

    mods = apply_scaling(self.vec_cc['scaling'], d["i"], self.vec_cc['step'],
                        self.vec_cc['bri'], self.vec_cc['con'], self.vec_cc['sat'],
                        self.vec_cc['r'], self.vec_cc['g'], self.vec_cc['b'])

    for i in range(batchSize):
        BRIGHTNESS = [source[i, 0], target[i, 0]]
        R = [source[i, 2], target[i, 2]]
        G = [source[i, 1], target[i, 1]]
        B = [source[i, 3], target[i, 3]]

        BRIGHTNESS[0] += BRIGHTNESS[1] * mods[0]
        BRIGHTNESS[0] += get_delta(BRIGHTNESS[0]) * mods[1]

        R[0] -= R[1] * mods[3]
        G[0] += G[1] * mods[4]
        B[0] -= B[1] * mods[5]

        R[0] *= mods[2]
        G[0] *= mods[2]
        B[0] *= mods[2]

    return original_callback(self, d)

Sampler.callback_state = cc_callback

def restore_callback():
    Sampler.callback_state = original_callback

script_callbacks.on_script_unloaded(restore_callback)
