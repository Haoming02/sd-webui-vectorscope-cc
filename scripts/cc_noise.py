from modules import devices
import torch

def get_delta(latent):
    mean = torch.mean(latent)
    return torch.sub(latent, mean)

def to_abs(latent):
    return torch.abs(latent)

def zeros(latent):
    return torch.zeros_like(latent)

def ones(latent):
    return torch.ones_like(latent)

def gaussian_noise(latent):
    return torch.rand_like(latent)

def normal_noise(latent):
    return torch.randn_like(latent)

def multires_noise(latent, use_zero:bool, iterations=8, discount=0.4):
    """
    Reference: https://wandb.ai/johnowhitaker/multires_noise/reports/Multi-Resolution-Noise-for-Diffusion-Model-Training--VmlldzozNjYyOTU2
    Credit: Kohya_SS
    """
    noise = zeros(latent) if use_zero else ones(latent)

    batchSize = noise.size(0)
    height = noise.size(2)
    width = noise.size(3)

    device = devices.get_optimal_device()
    upsampler = torch.nn.Upsample(size=(height, width), mode="bilinear").to(device)

    for b in range(batchSize):
        for i in range(iterations):
            r = torch.rand(1).item() * 2 + 2

            wn = max(1, int(width / (r**i)))
            hn = max(1, int(height / (r**i)))

            for c in range(4):
                noise[b, c] += upsampler(torch.randn(1, 1, hn, wn).to(device))[0, 0] * discount**i

            if wn == 1 or hn == 1:
                break

    return noise / noise.std()
