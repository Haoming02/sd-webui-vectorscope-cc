from modules.sd_samplers_kdiffusion import KDiffusionSampler
from modules import script_callbacks, devices
from scripts.cc_scaling import apply_scaling
from random import random
from torch import Tensor
import torch


class NoiseMethods:
    @staticmethod
    def get_delta(latent: Tensor) -> Tensor:
        mean = torch.mean(latent)
        return torch.sub(latent, mean)

    @staticmethod
    def to_abs(latent: Tensor) -> Tensor:
        return torch.abs(latent)

    @staticmethod
    def zeros(latent: Tensor) -> Tensor:
        return torch.zeros_like(latent)

    @staticmethod
    def ones(latent: Tensor) -> Tensor:
        return torch.ones_like(latent)

    @staticmethod
    def gaussian_noise(latent: Tensor) -> Tensor:
        return torch.rand_like(latent)

    @staticmethod
    def normal_noise(latent: Tensor) -> Tensor:
        return torch.randn_like(latent)

    @staticmethod
    def multires_noise(
        latent: Tensor, use_zero: bool, iterations: int = 8, discount: float = 0.4
    ):
        """
        Credit: Kohya_SS
        https://github.com/kohya-ss/sd-scripts/blob/main/library/custom_train_functions.py#L448
        """

        noise = NoiseMethods.zeros(latent) if use_zero else NoiseMethods.ones(latent)
        batchSize, c, w, h = noise.shape

        device = devices.get_optimal_device()
        upsampler = torch.nn.Upsample(size=(w, h), mode="bilinear").to(device)

        for b in range(batchSize):
            for i in range(iterations):
                r = random() * 2 + 2

                wn = max(1, int(w / (r**i)))
                hn = max(1, int(h / (r**i)))

                noise[b] += (upsampler(torch.randn(1, c, hn, wn).to(device)) * discount**i)[0]

                if wn == 1 or hn == 1:
                    break

        return noise / noise.std()


original_callback = KDiffusionSampler.callback_state

@torch.no_grad()
def cc_callback(self, d):
    if not self.vec_cc["enable"]:
        return original_callback(self, d)

    if getattr(self.p, "is_hr_pass", False) and not self.vec_cc["doHR"]:
        return original_callback(self, d)

    mode = str(self.vec_cc["mode"])
    method = str(self.vec_cc["method"])
    source = d[mode]

    if "Straight" in method:
        target = d[mode].detach().clone()
    elif "Cross" in method:
        target = d["x" if mode == "denoised" else "denoised"].detach().clone()
    elif "Multi-Res" in method:
        target = NoiseMethods.multires_noise(d[mode], "Abs" in method)
    elif method == "Ones":
        target = NoiseMethods.ones(d[mode])
    elif method == "N.Random":
        target = NoiseMethods.normal_noise(d[mode])
    elif method == "U.Random":
        target = NoiseMethods.gaussian_noise(d[mode])
    else:
        raise ValueError

    if "Abs" in method:
        target = NoiseMethods.to_abs(target)

    batchSize = int(d[mode].size(0))

    bri, con, sat, r, g, b = apply_scaling(
        self.vec_cc["scaling"],
        d["i"],
        self.vec_cc["step"],
        self.vec_cc["bri"],
        self.vec_cc["con"],
        self.vec_cc["sat"],
        self.vec_cc["r"],
        self.vec_cc["g"],
        self.vec_cc["b"],
    )

    for i in range(batchSize):
        # Brightness
        source[i][0] += target[i][0] * bri
        # Contrast
        source[i][0] += NoiseMethods.get_delta(source[i][0]) * con

        # R
        source[i][2] -= target[i][2] * r
        # G
        source[i][1] += target[i][1] * g
        # B
        source[i][3] -= target[i][3] * b

        # Saturation
        source[i][2] *= sat
        source[i][1] *= sat
        source[i][3] *= sat

    return original_callback(self, d)

KDiffusionSampler.callback_state = cc_callback


def restore_callback():
    KDiffusionSampler.callback_state = original_callback

script_callbacks.on_script_unloaded(restore_callback)
