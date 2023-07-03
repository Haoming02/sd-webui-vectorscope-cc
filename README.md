﻿# SD Webui Vectorscope CC
This is an Extension for the [Automatic1111 Webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui), which performs *a kind of* **Offset Noise**[*](#offset-noise-tldr) natively. 

> *This Extension is the result of my numerous trial and error[\*](#what-is-under-the-hood)*

## How to Use
After installing this Extension, you will see a new section in both **txt2img** and **img2img** tabs, 
refer to the parameters and sample images below and play around with the values.

**Note:** Since this modifies the underlying latent noise, the composition may change drastically.

#### Parameters
- **Enable:** Turn on & off this Extension
- **Alt:** Modify an alternative Tensor instead, causing the effects to be significantly stronger
- **Skip:** Skip the last percentage of steps and only process the first few steps

<p align="center"><img src="samples/Skip.jpg" width=512></p>
<p align="center">When <code>Alt.</code> is enabled, the image can get distorted at high value<br>Increase <code>Skip</code> to still achieve a stronger effect but without distortion</p>

- **Brightness:** Adjust the overall brightness of the image
- **Contrast:** Adjust the overall contrast of the image
- **Saturation:** Adjust the overall saturation of the image

#### Color Channels
<table>
    <thead align="center">
        <tr>
            <td><b>Channel</b></td>
            <td><b>Lower</b></td>
            <td><b>Higher</b></td>
        </tr>
    </thead>
    <tbody align="center">
        <tr>
            <td><b>R</b></td>
            <td>Cyan</td>
            <td>Red</td>
        </tr>
        <tr>
            <td><b>G</b></td>
            <td>Magenta</td>
            <td>Green</td>
        </tr>
        <tr>
            <td><b>B</b></td>
            <td>Yellow</td>
            <td>Blue</td>
        </tr>
    </tbody>
</table>

#### Advanced Settings

- **Process Hires. fix:** By default, this Extension only functions during the **txt2img** phase, so that **Hires. fix** may "fix" the artifacts introduced during **txt2img**. Enable this to process **Hires. fix** phase too.
  - This option does not affect **img2img**
  - **Note:** Keep the **txt2img** base `steps` higher than **Hires. fix** `steps` if you enable this

##### Noise Settings
> let `x` denote the Tensor ; let `y` denote the operations

<!-- "Straight", "Straight Abs.", "Cross", "Cross Abs.", "Ones", "N.Random", "U.Random", "Multi-Res", "Multi-Res Abs." -->

- **Straight:** All operations are calculated on the same Tensor
  - `x += x * y`
- **Cross:** All operations are calculated on the Tensor opposite of the `Alt.` setting
  - `x += x' * y`
- **Ones:** All operations are calculated on a Tensor filled with ones 
  - `x += 1 * y` 
- **N.Random:** All operations are calculated on a Tensor filled with random values from normal distribution 
  - `x += randn() * y`
- **U.Random:** All operations are calculated on a Tensor filled with random values from uniform distribution
  - `x += rand() * y`
- **Multi-Res:** All operations are calculated on a Tensor generated with multi-res noise algorithm
  - `x += multires() * y`
- **Abs.:** Calculate using the absolute values of the chosen Tensors instead
  - `x += abs(F) * y`

<p align="center"><img src="samples/Bright.jpg" width=768></p>
<p align="center"><img src="samples/Dark.jpg" width=768></p>


## Sample Images
- **Checkpoint:** [UHD-23](https://civitai.com/models/22371/uhd-23)
- **Pos. Prompt:** `(masterpiece, best quality), 1girl, solo, night, street, city, neon_lights`
- **Neg. Prompt:** `(low quality, worst quality:1.2)`, [`EasyNegative`](https://huggingface.co/datasets/gsdf/EasyNegative/tree/main), [`EasyNegativeV2`](https://huggingface.co/gsdf/Counterfeit-V3.0/tree/main/embedding)
- `Euler a`; `20 steps`; `7.5 CFG`; `Hires. fix`; `Latent (nearest)`; `16 H.steps`; `0.6 D.Str.`; `Seed:`**`3814649974`**
- `Straight Abs.`

<p align="center">
<b>Base</b><br>
<code>Extension Disabled</code><br>
<img src="samples/00.jpg" width=512>
</p>

<p align="center">
<b>Dark</b><br>
<code><b>Brightness:</b> -3; <b>Contrast:</b> 1.5</code><br>
<img src="samples/01.jpg" width=512>
</p>

<p align="center">
<b>Bright</b><br>
<code><b>Brightness:</b> 2.5; <b>Contrast:</b> 0.5; <b>Alt:</b> Enabled</code><br>
<img src="samples/02.jpg" width=512>
</p>

<p align="center">
<b>Chill</b><br>
<code><b>Brightness:</b> -2.5; <b>Contrast:</b> 1.25</code><br>
<code><b>R:</b> -1.5; <b>B:</b> 2.5</code><br>
<img src="samples/03.jpg" width=512>
</p>

<p align="center">
<b><s>Mexican Movie</s></b><br>
<code><b>Brightness:</b> 3; <b>Saturation:</b> 1.5</code><br>
<code><b>R:</b> 2; <b>G:</b> 1; <b>B:</b> -2</code><br>
<img src="samples/04.jpg" width=512>
</p>

<p align="center"><i>Notice the significant differences even when using the same seed</i></p>

## Roadmap
- [X] Extension Released
- [X] Add Support for **X/Y/Z Plot**
- [X] Implement different Noise functions
- [ ] Add Randomize functions
- [ ] Implement a better scaling algorithm
- [ ] Fix the Brightness issues
- [ ] Add Support for **Inpaint**
- [ ] Add Gradient feature
- [ ] Append Parameters onto Metadata

<p align="center"><img src="samples/XYZ.jpg" width=768></p>
<p align="center"><code>X/Y/Z Plot Support</code></p>

## Known Issues
- Does not work with `DDIM` sampler
- Has little effect when used with certain **LoRA**s
- Too high **Brightness** causes the image to be blurry; Too low **Brightness** causes the image to be noisy
  - Using `Multi-Res` seems to fix the blurry issue *(but not the noise issue)*
- Low `steps` *(`< 10`)* may cause the effects to be stronger due to poor scaling algorithm

<hr>

#### Offset Noise TL;DR
The most common *version* of **Offset Noise** you may have heard of is from this [blog post](https://www.crosslabs.org/blog/diffusion-with-offset-noise), 
where it was discovered that the noise functions used during **training** were flawed, causing `Stable Diffusion` to always generate images with an average of `0.5`.

> **ie.** Even if you prompt for dark/night or bright/snow, the overall image still looks "grey"

> [Technical Explanations](https://youtu.be/cVxQmbf3q7Q)

However, this Extension instead tries to offset the latent noise during the **inference** phase. 
Therefore, you do not need to use models that were specially trained, as this can work on any model.
Though, the results may not be as good as using properly trained models.

<hr>

#### What is Under the Hood
After reading through and messing around with the code, 
I found out that it is possible to directly modify the Tensors 
representing the latent noise used by the Stable Diffusion process.

The dimensions of the Tensors is `(X, 4, H / 8, W / 8)`, which can be thought of like this:

> **X** batch of noise images, with **4** channels, each with **(W / 8) x (H / 8)** values

> **eg.** Generating a single 512x768 image will create a Tensor of size (1, 4, 96, 64)

Then, I tried to play around with the values of each channel and ended up discovering these relationships.
Essentially, the 4 channels correspond to the **CMYK** color format, 
hence why you can control the brightness as well as the colors.

<hr>

#### Vectorscope?
The Extension is named this way because the color interactions remind me of the `Vectorscope` found in **Premiere Pro**'s **Lumetri Color**.
Those who are experienced in Color Correction should be rather familiar with this Extension.

<p align="center"><img src="samples/Vectorscope.png" width=256></p>

<sup>~~Yes. I'm aware that it's just how digital colors work in general.~~</sup>