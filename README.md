# SD Webui Vectorscope CC
This is an Extension for the [Automatic1111 Webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui), which performs *~~some kind of~~ **Offset Noise***[*](#offset-noise-tldr) natively.

**Note:** This Extension is the result of my numerous trial and error[*](#what-is-actually-under-the-hood). I have no idea how and why this works. 💀

## How to Use
After installing this Extension, you will a new section in both **txt2img** and **img2img** tabs. 
Refer to the parameters and sample images below, and play around with the values.

**Note:** Since this modifies the underlying latent noise, the composition may change drastically.

#### Parameters
- **Enable:** Turn on & off this Extension
- **Alt:** Modify an alternative Tensor. The effects are significantly stronger when this is **on**.
- **Brightness:** Adjust the overall brightness of the image
  - **Note:** Value too **high** causes the image to be blurry; Value too **low** causes extra noises to appear.
- **Contrast:** Adjust the overall contrast of the image
- **Saturation:** Adjust the overall saturation of the image
- **Skip:** Only process the first few steps and skip the rest, to combat the issues mentioned in **Brightness**

<table>
    <tbody>
        <tr align="center">
            <td>Parameter</td>
            <td>Decrease</td>
            <td>Increase</td>
        </tr>
        <tr align="center">
            <td>R</td>
            <td>Cyan</td>
            <td>Red</td>
        </tr>
        <tr align="center">
            <td>G</td>
            <td>Magenta</td>
            <td>Green</td>
        </tr>
        <tr align="center">
            <td>B</td>
            <td>Yellow</td>
            <td>Blue</td>
        </tr>
    </tbody>
</table>

## Sample Images
- **Checkpoint:** [UHD-23](https://civitai.com/models/22371/uhd-23)
- **Pos. Prompt:** `(masterpiece, best quality), 1girl, solo, night, street, city, neon_lights`
- **Neg. Prompt:** `(low quality, worst quality:1.2)`, [`EasyNegative`](https://huggingface.co/datasets/gsdf/EasyNegative/tree/main), [`EasyNegativeV2`](https://huggingface.co/gsdf/Counterfeit-V3.0/tree/main/embedding)
- `Euler a`; `20 steps`; `7.5 CFG`; `Hires. fix`; `Latent (nearest)`; `16 H.steps`; `0.6 D.Str.`; `Seed:`**`3814649974`**
- No offset noise Checkpoints/LoRAs were used

<p align="center"><b>Base</b><br>
Extension <code>Disabled</code><br>
<img src="samples/00.png" width=512></p>

<p align="center"><b>Dark</b><br>
<b>Brightness:</b><code>-2</code>; <b>Contrast:</b><code>1</code><br>
<img src="samples/01.png" width=512></p>

<p align="center"><b>Bright</b><br>
<b>Brightness:</b><code>1</code>; <b>Contrast:</b><code>-0.5</code>; <b>Alt:</b><code>Enabled</code><br>
<img src="samples/02.png" width=512></p>

<p align="center"><b>Chill</b><br>
<b>Brightness:</b><code>-2.5</code>; <b>Contrast:</b><code>1.5</code><br>
<b>R:</b><code>-0.5</code>; <b>B:</b><code>1</code><br>
<img src="samples/03.png" width=512></p>

<p align="center"><b><s>Mexican Movie</s></b><br>
<b>Brightness:</b><code>3</code>; <b>Contrast:</b><code>-1.5</code>; <b>Saturation:</b><code>1</code><br>
<b>R:</b><code>1</code>; <b>G:</b><code>0.5</code>; <b>B:</b><code>-2</code><br>
<img src="samples/04.png" width=512></p>

> Notice the significant difference even when using the same seed!

## Roadmap
- [X] Extension Released
- [ ] Add Support for **X/Y/Z Plot**
- [ ] Append Parameters onto Metadata

<hr>

#### Offset Noise TL;DR
It was [discovered](https://www.crosslabs.org/blog/diffusion-with-offset-noise) that, the noise functions used during training were flawed, causing Stable Diffusion to always generate images with an average brightness of `0.5`.

> **ie.** Even if you prompt for dark/night or bright/snow, the overall image still looks "grey" on average

> [Technical Explanations](https://youtu.be/cVxQmbf3q7Q)

<hr>

#### What is Actually Under the Hood
After reading through and messing around with the code, 
I found out that it is possible to modify the Tensors 
representing the latent noise used by the Stable Diffusion process.

The dimentions of the Tensors is `(1, 4, 64, 64)`, which can be thought of like this:

> **1** noise image, with **4** channels, each with **64x64** values

So I tried to play around with the values of each channel, 
and ended up discovering these relationships between channels and colors.
Thus, I wrote it as an Extension.

*~~And why does it work this way? IDK~~*

<hr>

#### Vectorscope?
The Extension is named this way because the color relations remind me of the `Vectorscope` in **Premiere Pro**.
Those who are experienced in Color Correction should be rather familiar with this Extension.

<p align="center"><img src="samples/Vectorscope.png" width=256></p>