from modules.sd_samplers_kdiffusion import KDiffusionSampler
from modules import script_callbacks, devices
from scripts.cc_scaling import apply_scaling
from random import random
import torch


class NoiseMethods:
    @staticmethod
    def get_delta(latent: torch.Tensor) -> torch.Tensor:
        mean = torch.mean(latent)
        return torch.sub(latent, mean)

    @staticmethod
    def to_abs(latent: torch.Tensor) -> torch.Tensor:
        return torch.abs(latent)

    @staticmethod
    def zeros(latent: torch.Tensor) -> torch.Tensor:
        return torch.zeros_like(latent)

    @staticmethod
    def ones(latent: torch.Tensor) -> torch.Tensor:
        return torch.ones_like(latent)

    @staticmethod
    def gaussian_noise(latent: torch.Tensor) -> torch.Tensor:
        return torch.rand_like(latent)

    @staticmethod
    def normal_noise(latent: torch.Tensor) -> torch.Tensor:
        return torch.randn_like(latent)

    @staticmethod
    @torch.inference_mode()
    def multires_noise(
        latent: torch.Tensor, use_zero: bool, iterations: int = 8, discount: float = 0.4
    ):
        """
        Credit: Kohya_SS
        https://github.com/kohya-ss/sd-scripts/blob/v0.8.5/library/custom_train_functions.py#L448
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

                noise[b] += (
                    upsampler(torch.randn(1, c, hn, wn).to(device)) * discount**i
                )[0]

                if wn == 1 or hn == 1:
                    break

        return noise / noise.std()


def RGB_2_CbCr(r: float, g: float, b: float) -> float:
    """Convert RGB channels into YCbCr for SDXL"""
    cb = -0.15 * r - 0.29 * g + 0.44 * b
    cr = 0.44 * r - 0.37 * g - 0.07 * b

    return cb, cr


original_callback = KDiffusionSampler.callback_state


@torch.inference_mode()
def cc_callback(self, d):
    if not self.vec_cc["enable"]:
        return original_callback(self, d)

    if getattr(self.p, "is_hr_pass", False) and not self.vec_cc["doHR"]:
        return original_callback(self, d)

    if getattr(self.p, "_ad_inner", False) and not self.vec_cc["doAD"]:
        return original_callback(self, d)

    is_xl: bool = self.p.sd_model.is_sdxl

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

    if not is_xl:
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

    else:
        # But why...
        cb, cr = RGB_2_CbCr(r, b, g)

        for i in range(batchSize):
            # Brightness
            source[i][0] += target[i][0] * bri
            # Contrast
            source[i][0] += NoiseMethods.get_delta(source[i][0]) * con

            # CbCr
            source[i][1] -= target[i][1] * cr
            source[i][2] += target[i][2] * cb

            # Saturation
            source[i][1] *= sat
            source[i][2] *= sat

    return original_callback(self, d)


KDiffusionSampler.callback_state = cc_callback


def restore_callback():
    KDiffusionSampler.callback_state = original_callback


script_callbacks.on_script_unloaded(restore_callback)
